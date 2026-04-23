# Amaznt Backend

Backend API for **Amazn't**, a community platform where users share, browse, and discuss failed or hilariously bad purchases.  
The core idea is simple: turn regrettable shopping decisions into searchable, discussable community content with a **Rubbish Score**.

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

## Main Goals
## MVP Roadmap

| Version | Goal | Scope | Outcome |
|---|---|---|---|
| MVP v1 | Build the foundation | FastAPI setup, PostgreSQL, SQLAlchemy, Alembic, User model, registration, login, `/auth/me`, basic posts/comments, local run, smoke tests | A working backend with authentication and core CRUD skeleton |
| MVP v2 | Expand community behavior | Reactions, rubbish score, ranking, reports, moderation, notifications, image upload, stronger tests | A more interactive community backend with richer user behavior |
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

### In Progress

| Feature | Status | Notes |
|---|---|---|
| Auth endpoint tests | In progress | pytest skeleton next |
| README and API docs | In progress | Project documentation is being cleaned up |

### Planned

| Feature | Status | Notes |
|---|---|---|
| Post model and CRUD | Planned | Main content layer |
| Comment CRUD | Planned | User discussion layer |
| Reaction / rubbish score | Planned | Core project identity |
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
