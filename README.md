# Amazn't Backend

Backend API for **Amazn't**, a community platform where users share, browse, and discuss failed or hilariously bad purchases.  
The core idea is simple: turn regrettable shopping decisions into searchable, discussable community content with a **Buyer Regret Score**.

## Overview

Amaznt started as a CRUD practice project, but I wanted it to cover the backend work that tutorials often skip: authentication, async database access, migrations, Docker setup, testing, and debugging real issues.

## Why I Built This

A lot of tutorial projects stop at simple CRUD.  
I wanted to build a backend project that also covers the parts that matter in production:

- authentication and protected routes
- async database access
- schema and model separation
- migration management
- troubleshooting real implementation issues
- testing and deployment preparation

## MVP Roadmap

| Version | Goal | Scope | Outcome |
|---|---|---|---|
| MVP v1 | Build the foundation | FastAPI setup, PostgreSQL, SQLAlchemy, Alembic, User model, registration, login, `/auth/me`, Product Fail Post CRUD, Buyer Regret Score v1, local run, smoke tests | A working backend with authentication, post CRUD, and regret score calculation |
| MVP v2 | Expand community behavior | Comments, reactions, Buyer Regret Score v2, ranking, reports, moderation, image upload, stronger tests | A more interactive community backend with richer user behavior |
| MVP v3 | Production readiness | Redis cache, rate limiting, GitHub Actions, deployment, performance tuning, documentation polish | A backend that is easier to run, test, deploy, and explain in a portfolio review |

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Language | Python |
| Validation / Schemas | Pydantic |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy (async) |
| DB Driver | asyncpg |
| Migrations | Alembic |
| Authentication | JWT + OAuth2PasswordBearer |
| Password Hashing | pwdlib with Argon2 |
| API Docs | Swagger / OpenAPI |
| Containerization / Local Dev | Docker, Docker Compose |
| Planned Infra | GitHub Actions, AWS EC2, Nginx, HTTPS |

## Current Features

### Implemented

| Feature | Status | Notes |
|---|---|---|
| FastAPI project setup | Done | Modular backend structure in place |
| PostgreSQL integration | Done | Async SQLAlchemy sessions with asyncpg |
| Alembic migrations | Done | Schema versioning is set up |
| User model | Done | Includes `username`, `email`, `role`, `bio`, `created_at`, `is_active` |
| Schema refactor | Done | Pydantic schemas moved into `app/schemas/` |
| User registration | Done | Password hashing included |
| Login flow | Done | JWT access token is issued |
| `/auth/me` endpoint | Done | Uses `OAuth2PasswordBearer`, `get_current_user()`, `get_current_active_user()` |
| Product Fail Post CRUD | Done | Authenticated users can create, read, update, and delete failed purchase posts |
| Buyer Regret Score v1 | Done | Weighted score calculation with normalized 1-5 inputs and grade output |
| Comment APIs | Done | Users can create, list, and delete comments with author authorization |
| Local image upload | Done | Post authors can upload image evidence to local `media/` storage |
| Image retrieval | Done | Post detail responses include images, and images can be listed separately |
| Static media serving | Done | Uploaded files are served through `/media/...` using FastAPI `StaticFiles` |
| Image deletion | Done | Post authors can delete image metadata and local image files |
| Core post/comment/image tests | In progress | Main success and authorization cases are covered; edge cases are still being expanded |
| Docker local environment | Done | FastAPI app and PostgreSQL run together with Docker Compose |
| Docker migration workflow | Done | Alembic can run inside the app container against Docker PostgreSQL |


### Planned

| Feature | Status | Notes |
|---|---|---|
| Reaction system | Planned | Community feedback for v2 score calculation |
| Ranking / popular posts | Planned | Community engagement layer |
| Admin / moderation features | Planned | Reporting and control |
| Redis caching and rate limiting | Planned | Performance and abuse control |
| GitHub Actions CI | Planned | Automated checks |
| EC2 + Nginx + HTTPS | Planned | Deployment and production setup |
| Performance analysis | Planned | Query optimization and tuning |

## Project Structure

```text
app/
├── api/
├── core/
├── models/
├── schemas/
├── services/
└── database/
```

This keeps database models and API request/response shapes from getting mixed together.

## Docker Local Setup

The recommended local MVP setup uses Docker Compose to run the FastAPI app and PostgreSQL together.

### 1. Create environment file

Copy the example environment file:

```bash
cp .env.example .env
```

Update values in `.env` if needed.

### 2. Start the app and database

```bash
docker compose up --build
```

This starts:

```text
amaznt-backend-app       FastAPI app container
amaznt-backend-postgres  PostgreSQL 16 container
```

The API will be available at:

```text
http://localhost:8000
```

Swagger docs:

```text
http://localhost:8000/docs
```

### 3. Run database migrations

In another terminal, run:

```bash
docker compose exec app alembic upgrade head
```

### 4. Verify the app

```bash
curl http://localhost:8000/health
```

Expected result:

```json
{"status":"ok"}
```

### 5. Stop containers

```bash
docker compose down
```

PostgreSQL data is stored in the Docker volume `postgres_data`, so database data persists across normal container restarts.

## Environment Variables

This project uses `.env` for local configuration. Start from `.env.example`:

```bash
cp .env.example .env
```

Important variables:

| Variable | Purpose |
|---|---|
| `APP_NAME` | FastAPI application title |
| `DEBUG` | Enables debug mode when set to `true` |
| `SECRET_KEY` | JWT signing secret |
| `ALGORITHM` | JWT algorithm, usually `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT access token lifetime |
| `DATABASE_URL` | Local database URL used when running the app outside Docker |
| `POSTGRES_USER` | PostgreSQL user created by Docker Compose |
| `POSTGRES_PASSWORD` | PostgreSQL password created by Docker Compose |
| `POSTGRES_DB` | PostgreSQL database name created by Docker Compose |
| `DOCKER_DATABASE_URL` | Database URL used by the app container to connect to the `postgres` service |

### Local vs Docker database URL

When running outside Docker, the app can use a local PostgreSQL URL:

```text
postgresql+asyncpg://uki@localhost:5432/amaznt
```

When running inside Docker Compose, the app must use the Compose service name:

```text
postgresql+asyncpg://amaznt_user:amaznt_password@postgres:5432/amaznt
```

Inside a Docker container, `localhost` means the container itself. To connect from the app container to the PostgreSQL container, use the service name `postgres`.

Docker Compose injects the Docker database URL into the app container:

```yaml
environment:
  DATABASE_URL: ${DOCKER_DATABASE_URL}
```

## Buyer Regret Score

Buyer Regret Score is the main feature of this project. In MVP v1, the score is calculated from user-entered regret inputs:

- `value_regret_score`
- `description_mismatch_score`
- `quality_disappointment_score`
- `funniness_score`
- `anger_score`

Each input is accepted on a 1-5 scale and normalized to a 20-100 scale.

```text
1 -> 20
2 -> 40
3 -> 60
4 -> 80
5 -> 100
```

The v1 formula currently implemented in `app/services/product_fail_score_service.py` is:

```text
final_score =
  value_regret_score * 0.30
+ description_mismatch_score * 0.25
+ quality_disappointment_score * 0.20
+ funniness_score * 0.10
+ anger_score * 0.15
```

Current calculation version:

```text
fail_score_v1
```

Grades:

| Score range | Grade |
|---|---|
| 0-20 | Level 1 - Somehow Fine |
| 21-40 | Level 2 - Mild Regret |
| 41-60 | Level 3 - Wallet Bruised |
| 61-80 | Level 4 - Proper Letdown |
| 81-95 | Level 5 - Absolute Rubbish |
| 96-100 | Level 6 - Hall of Shame |

The calculated score is stored in `product_fail_scores` with a grade and `calculation_version`, so future score formulas can be introduced without losing track of how older scores were calculated.

## API Summary

### System

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Root endpoint for basic app status |
| `GET` | `/health` | Health check endpoint |

### Auth

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Log in and receive a JWT access token |
| `GET` | `/auth/me` | Get the current authenticated user |

### Posts

| Method | Path | Description |
|---|---|---|
| `POST` | `/posts` | Create a failed purchase post and calculate Buyer Regret Score |
| `GET` | `/posts` | List posts with pagination |
| `GET` | `/posts/{post_id}` | Get one post with score and uploaded images |
| `PATCH` | `/posts/{post_id}` | Update a post and optionally recalculate score |
| `DELETE` | `/posts/{post_id}` | Delete a post owned by the current user |

### Comments

| Method | Path | Description |
|---|---|---|
| `POST` | `/posts/{post_id}/comments` | Create a comment on a post |
| `GET` | `/posts/{post_id}/comments` | List comments for a post |
| `DELETE` | `/posts/{post_id}/comments/{comment_id}` | Delete a comment owned by the current user |

### Images

| Method | Path | Description |
|---|---|---|
| `POST` | `/posts/{post_id}/images` | Upload one image for a post owned by the current user |
| `GET` | `/posts/{post_id}/images` | List uploaded images for a post |
| `DELETE` | `/posts/{post_id}/images/{image_id}` | Delete one image from a post owned by the current user |
| `GET` | `/media/post-images/{post_id}/{stored_filename}` | Serve an uploaded image file through `StaticFiles` |

## Local Image Upload Policy

Images are stored locally for the MVP. The database stores image metadata, while the actual files are saved under the `media/` directory.

```text
media/post-images/{post_id}/{stored_filename}
```

Current upload rules:

- One image per request
- Up to 5 images per post
- Allowed extensions: `.jpg`, `.jpeg`, `.png`, `.webp`
- Allowed content types: `image/jpeg`, `image/png`, `image/webp`
- Max file size: 5MB
- Empty files are rejected
- Only the post author can upload or delete images

Uploaded files are served locally through FastAPI `StaticFiles`:

```text
/media/post-images/{post_id}/{stored_filename}
```

This local media setup is for MVP development. In a production version, this responsibility should move to object storage such as AWS S3.

## Testing

The project uses `pytest` with FastAPI `TestClient`.

Current test coverage includes:

- post creation with and without authentication
- Buyer Regret Score validation
- comment deletion by owner and non-author
- image upload helper flow
- image deletion by owner and non-author
- post detail response including uploaded images

Run tests with:

```bash
pytest
```

## Troubleshooting Notes

### 1. Alembic in Docker connected to the wrong database

**Problem**  
Alembic failed when I tried to run migrations inside the Docker app container. It was still trying to connect to a local `localhost` database.

**Cause**  
Inside Docker, `localhost` means the current container itself. Since PostgreSQL runs in a separate `postgres` container, the app container has to connect through the Compose service name `postgres`.

**Fix**  
I updated `alembic/env.py` so Alembic reads `DATABASE_URL` from the runtime environment. The app still uses `asyncpg`, but Alembic converts that URL to `psycopg2` because the current migration setup runs through a sync SQLAlchemy engine.

### 2. `users.created_at` failed because the database default was missing

**Problem**  
User registration failed because `users.created_at` was `NOT NULL`, but PostgreSQL did not have a database-level default for that column.

**Cause**  
The SQLAlchemy model had `server_default=func.now()`, but the migration that had already been applied to the database did not create the same default. The model and the real database schema had drifted.

**Fix**  
I added a new Alembic migration to set `users.created_at` to `server_default=now()`. I did this as a new migration instead of editing old migration history.

### 3. Post deletion failed because child rows still referenced `posts.id`

**Problem**  
`DELETE /posts/{post_id}` failed with a foreign key violation. The post still had related rows in `product_fail_scores`, `comments`, and `post_images`.

**Cause**  
Those tables referenced `posts.id`, but the existing foreign key constraints did not have `ON DELETE CASCADE`. PostgreSQL correctly blocked the parent row from being deleted while child rows still pointed to it.

**Fix**  
I added `ondelete="CASCADE"` to the SQLAlchemy models and created a migration that drops and recreates the existing PostgreSQL foreign key constraints with `ON DELETE CASCADE`. The API still deletes physical image files itself because database cascade only removes database rows, not files on disk.

### 4. Auth smoke tests used different data after switching to Docker

**Problem**  
A login that worked against the local database returned `401 Unauthorized` after switching to the Docker environment.

**Cause**  
The local PostgreSQL database and the Docker PostgreSQL database are separate databases. A test user created in the local DB does not automatically exist in the Docker DB.

**Fix**  
For Docker-based smoke tests, I create or register test users in the Docker PostgreSQL database instead of assuming local DB data exists there.
