# Amaznt Backend

Backend API for **Amazn't**, a community platform where users share, browse, and discuss failed or hilariously bad purchases.  
The core idea is simple: turn regrettable shopping decisions into searchable, discussable community content with a **Buyer Regret Score**.

## Overview

Amaznt is a FastAPI backend project built to go beyond basic CRUD practice.  
It focuses on real backend concerns such as authentication, async database access, migrations, testing, caching, deployment, and performance tuning through a structured 16-week roadmap.

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
| MVP v3 | Production readiness | Redis cache, rate limiting, Docker, GitHub Actions, deployment, performance tuning, documentation polish | A portfolio-ready backend with operational and performance maturity |

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
| Planned Infra | Docker, GitHub Actions, AWS EC2, Nginx, HTTPS |

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

### Planned

| Feature | Status | Notes |
|---|---|---|
| Reaction system | Planned | Community feedback for v2 score calculation |
| Ranking / popular posts | Planned | Community engagement layer |
| Admin / moderation features | Planned | Reporting and control |
| Redis caching and rate limiting | Planned | Performance and abuse control |
| Docker-based local environment | Planned | Dev consistency |
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

This project separates ORM models from Pydantic schemas so database objects and API contracts stay clear and maintainable.

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

The v1 formula is:

```text
final_score =
  value_regret_score * 0.25
+ description_mismatch_score * 0.30
+ quality_disappointment_score * 0.25
+ funniness_score * 0.10
+ anger_score * 0.10
```

The calculated score is stored in `product_fail_scores` with a grade and `calculation_version`, so future score formulas can be introduced without losing track of how older scores were calculated.

## API Summary

### Auth

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/register-test` | Register a new user |
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
