# Troubleshooting and Engineering Decisions

This document records production-style problems encountered while building the Amazn't backend. It intentionally avoids minor syntax mistakes or one-off endpoint confusion. The focus is on issues that affected database correctness, local environment reliability, test stability, domain modeling, or public API behavior.

## 1. Alembic Connected to the Wrong Database in Docker

### Problem

Alembic failed when migrations were run inside the Docker app container. The migration process was still trying to connect to a local `localhost` database instead of the PostgreSQL container.

### Why It Matters

Local development and Docker development used different network contexts. A migration command that works outside Docker can fail inside Docker if the database host is not resolved correctly. This can block setup, onboarding, and deployment-style smoke testing.

### Root Cause

Inside a Docker container, `localhost` refers to the container itself. The PostgreSQL database runs in a separate Compose service, so the app container must connect through the Compose service name, `postgres`.

The migration setup also needed to read the runtime `DATABASE_URL` instead of assuming the local development URL.

### Options Considered

- Keep a separate Alembic config for Docker.
- Hardcode the Docker database URL in `alembic.ini`.
- Read `DATABASE_URL` from the runtime environment and let Docker Compose inject the correct URL.

### Solution

Alembic was updated to read `DATABASE_URL` from the environment. Docker Compose provides the Docker-specific URL through `DOCKER_DATABASE_URL`, while local development can continue using the local database URL.

The app still uses an async SQLAlchemy URL with `asyncpg`, while the migration setup converts it for Alembic's synchronous engine path.

### Implementation Notes

Relevant files:

```text
alembic/env.py
docker-compose.yml
.env
.env.example
```

Important distinction:

```text
Local DB host: localhost
Docker DB host: postgres
```

### Verification

The Docker migration workflow was verified by running Alembic from inside the app container against the Docker PostgreSQL service.

### Interview Summary

I hit a Docker-specific migration issue because `localhost` inside the app container did not point to the PostgreSQL container. I fixed it by making Alembic read the runtime `DATABASE_URL`, allowing local and Docker environments to use the correct database host without hardcoding environment-specific values.

## 2. Database Schema Drift on `users.created_at`

### Problem

User registration failed because the `users.created_at` column was `NOT NULL`, but the actual PostgreSQL schema did not have a database-level default for that column.

### Why It Matters

SQLAlchemy model definitions and the real database schema can drift over time. If the code assumes a database default exists but the applied migration did not create it, normal application writes can fail at runtime.

### Root Cause

The SQLAlchemy model included `server_default=func.now()`, but the already-applied migration history did not create the matching database default.

The model looked correct, but the real database schema was missing the default.

### Options Considered

- Edit the old migration.
- Manually alter the local database.
- Add a new migration that brings the database schema back in line with the model.

### Solution

A new Alembic migration was added to set `users.created_at` to use a database-level `now()` default. This preserved migration history and avoided editing old migrations that may already have been applied elsewhere.

### Implementation Notes

The fix followed the rule:

```text
Do not rewrite applied migration history.
Add a forward migration to repair schema drift.
```

### Verification

User registration was re-tested after applying the migration, and the database was able to populate `created_at` automatically.

### Interview Summary

I found a schema drift issue where the SQLAlchemy model had a server default, but the actual database did not. Instead of editing old migration history, I created a new migration to align the database with the model and restore registration behavior.

## 3. Post Deletion Failed Because Child Rows Still Referenced the Post

### Problem

Deleting a post failed with a foreign key violation because related rows still referenced `posts.id`.

Affected child data included:

```text
product_fail_scores
comments
post_images
post_reactions
post_verdicts
```

### Why It Matters

Deleting a parent entity in a relational database must account for dependent rows. Without a clear deletion policy, the API can fail at runtime or leave orphaned data.

### Root Cause

Some foreign key constraints did not have `ON DELETE CASCADE`, so PostgreSQL correctly blocked deletion of the parent `posts` row while child rows still existed.

### Options Considered

- Delete child rows manually in the API before deleting the post.
- Use ORM relationship cascade only.
- Add database-level `ON DELETE CASCADE` to the relevant foreign keys.

### Solution

Database-level cascade delete was applied to child tables that are owned by a post. SQLAlchemy models were updated with `ondelete="CASCADE"`, and migrations were added to recreate the relevant constraints.

For image files, the API still deletes physical files explicitly, because database cascade only removes database rows and cannot remove files from local storage.

### Implementation Notes

Relevant model pattern:

```text
ForeignKey("posts.id", ondelete="CASCADE")
```

Important distinction:

```text
Database cascade removes child rows.
Application logic removes physical image files.
```

### Verification

Post deletion was verified with related score, comment, image metadata, reaction, and verdict data present.

### Interview Summary

Post deletion initially failed because child rows still referenced the post. I fixed it by moving ownership cleanup into database constraints with `ON DELETE CASCADE`, while keeping file deletion in the application layer because the database cannot delete local files.

## 4. Async SQLAlchemy Engine Caused TestClient Event Loop Issues

### Problem

Some tests used normal synchronous `TestClient`, but the app internally ran async FastAPI endpoints with an async SQLAlchemy engine. This created connection cleanup issues between tests.

### Why It Matters

Tests can look synchronous while still exercising async infrastructure. If an async database engine keeps connections tied to an old event loop, later tests can fail for reasons unrelated to business logic.

### Root Cause

`TestClient` hides the async execution model from the test function, but the app still uses async DB sessions and async connection pools. Connections can remain attached to an event loop after a test finishes.

### Options Considered

- Rewrite all API tests as async tests.
- Create a separate test database engine per test.
- Dispose the shared async engine after each `TestClient` test.

### Solution

The test suite disposes the async SQLAlchemy engine after each test.

```python
@pytest.fixture(autouse=True)
def dispose_database_engine_after_test():
    yield
    anyio.run(database_engine.dispose)
```

### Implementation Notes

This fixture does not reset test data. It only closes the async connection pool so the next test starts with clean DB connections.

Relevant files:

```text
tests/test_posts.py
tests/test_rankings.py
```

### Verification

Focused API tests for posts, reactions, verdicts, and rankings were able to run without event loop connection errors after disposing the engine.

### Interview Summary

Although the tests use synchronous `TestClient`, the app still runs async endpoints and async SQLAlchemy under the hood. I added engine disposal after each test to prevent async connection pool state from leaking between event loops.

## 5. Ranking Tests Were Affected by Existing Database Data

### Problem

Ranking tests could become unstable when older data already existed in the database. A newly created test post was not always guaranteed to appear where the test expected if the ranking endpoint returned many existing posts.

### Why It Matters

Ranking tests must be deterministic. If they depend on the current contents of a shared development database, they can pass or fail depending on unrelated data.

### Root Cause

The ranking endpoint sorted across all matching posts. Existing high-score or recently created posts could appear before the newly created test data, especially when using broad periods like `all_time`.

### Options Considered

- Clear the database before every ranking test.
- Use a fully isolated test database.
- Make test assertions focus on deterministic conditions created inside the test.

### Solution

The tests were kept focused on clear ranking behavior:

- invalid period returns `422`
- response shape is stable
- a created high-score post appears at the expected top position for Buyer Regret ranking
- Wallet Saved ranking orders posts by `estimated_money_saved`

For Wallet Saved ranking, the test creates two posts with the same saved count but different prices, proving that the ranking is based on money saved rather than raw reaction count.

### Implementation Notes

Relevant endpoint:

```text
GET /rankings/buyer-regret
GET /rankings/wallet-saved
```

Relevant tests:

```text
tests/test_rankings.py
```

### Verification

Ranking tests were written to create their own posts and reactions before calling the ranking endpoints.

### Interview Summary

The ranking tests were vulnerable to existing database data, so I changed the tests to verify deterministic ranking behavior using data created inside the test. This made the tests focus on the ranking contract instead of depending on the current state of the development database.

## 6. Separating Product Failure Severity from Post Impact

### Problem

The project has multiple community signals, but not all signals should affect the same metric. In particular, `SAVED_MY_MONEY` could be mistaken as a signal for product failure severity.

### Why It Matters

Mixing signals with different meanings can make metrics hard to explain and easy to manipulate. A post can help users save money without necessarily proving that the product failure is more severe.

### Root Cause

Community reactions have different domain meanings:

```text
HELPFUL -> usefulness / confidence
SAME_HERE -> repeated product failure experience
SAVED_MY_MONEY -> purchase avoidance / money saved impact
AGREE / DISAGREE -> community validation of the product failure claim
```

Using all of them in one score would blur the difference between product severity, trust, popularity, and economic impact.

### Options Considered

- Use all reactions in Buyer Regret Score v2.
- Use only verdicts in Buyer Regret Score v2.
- Use `SAME_HERE`, `AGREE`, and `DISAGREE` for v2, and reserve `SAVED_MY_MONEY` for money-saved impact.

### Solution

Buyer Regret Score v2 uses:

```text
author_score
SAME_HERE
AGREE
DISAGREE
```

It excludes:

```text
SAVED_MY_MONEY
```

`SAVED_MY_MONEY` is dedicated to:

```text
estimated_money_saved = saved_my_money_count * price_paid
GET /rankings/wallet-saved
```

### Implementation Notes

Relevant files:

```text
app/services/buyer_regret_score_service.py
app/services/money_saved_service.py
app/api/rankings.py
docs/buyer_regret_score_v2.md
```

### Verification

Service tests cover Buyer Regret Score v2 behavior, and ranking tests cover Wallet Saved ranking behavior.

### Interview Summary

I separated product failure severity from post impact. Buyer Regret Score v2 uses validation signals like `SAME_HERE`, `AGREE`, and `DISAGREE`, while `SAVED_MY_MONEY` is reserved for `estimated_money_saved` and Wallet Saved ranking.

## 7. Wallet Saved Ranking Needed Money-Based Sorting, Not Reaction Count Sorting

### Problem

Wallet Saved ranking could be incorrectly sorted by raw `saved_my_money_count`.

### Why It Matters

Raw count does not represent economic impact. A small number of avoided expensive purchases can save more money than many avoided cheap purchases.

Example:

```text
Post A: 10 users * 1,000 = 10,000
Post B: 2 users * 100,000 = 200,000
```

Post B should rank higher even though it has fewer saved-money reactions.

### Root Cause

The raw reaction count is only one side of the formula. The ranking's domain meaning is based on money saved:

```text
estimated_money_saved = saved_my_money_count * price_paid
```

### Options Considered

- Sort by `saved_my_money_count`.
- Sort by `price_paid`.
- Sort by calculated `estimated_money_saved`, with count and creation time as tie-breakers.

### Solution

Wallet Saved ranking sorts by:

```text
estimated_money_saved DESC
saved_my_money_count DESC
created_at DESC
```

### Implementation Notes

Relevant endpoint:

```text
GET /rankings/wallet-saved
```

Relevant response fields:

```text
saved_my_money_count
estimated_money_saved
```

### Verification

The ranking test creates two posts with equal `SAVED_MY_MONEY` count but different prices. The more expensive post must appear first, proving the endpoint sorts by `estimated_money_saved` instead of count alone.

### Interview Summary

I made Wallet Saved ranking sort by `estimated_money_saved`, not raw reaction count. This better matches the feature's purpose because the ranking should reflect economic impact, not just how many users clicked a reaction.

## Future Troubleshooting Topics

The following production-style issues are expected during Week 9 and should be added after implementation:

- Small-sample bias in category risk rankings
- Read-time Buyer Regret Score v2 aggregation trade-offs in category risk rankings
- Duplicate report prevention with a database-level uniqueness constraint
- Hidden posts still affecting public lists or rankings
- Admin-only moderation actions through RBAC
