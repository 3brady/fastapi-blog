# FastAPI Blog

> A full-stack blog with a JSON API and a server-rendered frontend, built on
> FastAPI, async SQLAlchemy, and Postgres — JWT auth, password reset emails,
> profile pictures, and a paginated feed in one Docker image.

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.14-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.141-009688?style=flat-square&logo=fastapi&logoColor=white" />
  <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" />
  <img alt="SQLAlchemy" src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat-square" />
  <img alt="uv" src="https://img.shields.io/badge/uv-managed-8BD5CA?style=flat-square&logo=uv" />
  <img alt="Docker" src="https://img.shields.io/badge/Docker-ready-2496ED?style=flat-square&logo=docker&logoColor=white" />
  <img alt="Ruff" src="https://img.shields.io/badge/lint-Ruff-D7FF64?style=flat-square" />
  <img alt="pytest" src="https://img.shields.io/badge/test-pytest-0A9EDC?style=flat-square" />
</p>

## Table of Contents

- [Features](#features)
- [Disabled in Production](#disabled-in-production)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Docker](#docker)
- [Environment Variables](#environment-variables)
- [Database Migrations](#database-migrations)
- [API Reference](#api-reference)
- [Pages](#pages)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [Deployment](#deployment)
- [Contributing](#contributing)

## Features

- **User accounts** — register, OAuth2 password login, JWT sessions, editable profile
- **Posts** — create, read, full and partial update, and delete, with ownership enforced server-side
- **Pagination** — offset/limit API with `has_more` and a "Load More" infinite-style feed
- **Password recovery** — email-based reset with single-use, hashed, expiring tokens
- **Profile pictures** — upload (JPEG/PNG/GIF/WebP, max 5 MB), auto-crop to 300x300, and delete
- **Security** — argon2 password hashing, JWT with required `exp`/`sub`, hashed tokens, hardened HTTP headers, HTML/JSON-aware error handlers, client-side output escaping
- **Theme** — Bootstrap light/dark/auto toggle persisted in `localStorage`
- **Observability** — `/health` endpoint reporting database availability

## Disabled in Production

The password reset and profile picture endpoints fully exist in the backend and
once worked end-to-end, but their buttons are **hidden on the deployed site**.
They depend on two things free serverless hosting (Vercel) can't reliably
provide: email delivery and persistent file storage.

- **Password reset** — the "Forgot your password?" link in `templates/login.html`
  is removed. The `/api/users/forgot-password` and `/api/users/reset-password`
  endpoints still work if called directly.
- **Profile pictures** — the upload/delete section in `templates/account.html`
  is hidden with `d-none`. The `/api/users/{user_id}/picture` endpoints still
  work if called directly. User uploads won't survive Vercel's ephemeral disk.

### How to enable locally

Both features work fine on a normal machine:

1. Re-add `<a href="{{ url_for("forgot_password_page") }}">Forgot your password?</a>`
   under the login form in `templates/login.html`.
2. Remove the `d-none` class from the Profile Picture section header in
   `templates/account.html`.
3. For password resets, configure email in `.env`:

   ```
   RESEND_API_KEY=re_...
   RESEND_FROM=onboarding@resend.dev
   FRONTEND_URL=http://localhost:8000
   ```

   Note: `onboarding@resend.dev` only delivers to the email address on your
   Resend account. To reach arbitrary recipients, verify a domain in Resend and
   set `RESEND_FROM` to an address on it.
4. Profile pictures are stored locally in `media/profile_pics/` — that just
   works with no extra setup.

## Tech Stack

| Layer      | Technology                                          |
| ---------- | --------------------------------------------------- |
| Framework  | FastAPI (async)                                     |
| Data       | SQLAlchemy 2.0 async ORM + Alembic migrations       |
| Database   | PostgreSQL (async via psycopg)                      |
| Auth       | PyJWT + `pwdlib[argon2]` + OAuth2 password flow     |
| Templates  | Jinja2 + Bootstrap 5                                |
| Images     | Pillow                                              |
| Email      | Resend API
| Frontend   | Vanilla JS modules + CSS                            |
| Tooling    | uv, ruff, pytest, multi-stage Docker                |

## Quick Start

### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)
- A PostgreSQL database (or a [Neon](https://neon.tech) project) and, for
  password resets, a [Resend](https://resend.com) API key

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/3brady/full_stack.git
cd full_stack

# 2. Install dependencies (dev group included by default)
uv sync

# 3. Configure environment — copy the example and fill it in
cp .env.example .env

# 4. Apply database migrations
uv run alembic upgrade head

# 5. Run the app
uv run fastapi dev
```

Open http://localhost:8000 — the UI and the API share the same origin, and
interactive API docs live at `/docs`.

## Docker

The application ships as a multi-stage image managed with `uv`, running as a
non-root user on port `8080` (override with `$PORT`).

```bash
# Build
docker build -t fastapi-blog .

# Run migrations against the target database first
docker run --rm --env-file .env --entrypoint alembic fastapi-blog upgrade head

# Run
docker run -p 8080:8080 --env-file .env fastapi-blog
```

## Environment Variables

Configuration is loaded from `.env` (see `.env.example`) via Pydantic settings.
Every variable must be provided on the host — the `.env` file is gitignored and
excluded from the Docker build.

| Variable                    | Required | Default                          | Description                          |
| --------------------------- | -------- | -------------------------------- | ------------------------------------ |
| `SECRET_KEY`                | Yes      | —                                | JWT signing secret (`python -c "import secrets; print(secrets.token_hex(32))"`) |
| `DATABASE_URL`              | Yes      | —                                | Async SQLAlchemy URL (`postgresql+psycopg://...`) |
| `ALGORITHM`                 | No       | `HS256`                          | JWT algorithm                        |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No     | `30`                             | Access token lifetime                |
| `MAX_UPLOAD_SIZE_BYTES`     | No       | `5242880` (5 MB)                 | Profile picture size limit           |
| `POSTS_PER_PAGE`            | No       | `10`                             | Posts per page / default API limit   |
| `RESET_TOKEN_EXPIRE_MINUTES` | No      | `60`                             | Password reset token lifetime        |
| `RESEND_API_KEY`            | No       | `""`                             | Resend API key (required to send email) |
| `RESEND_FROM`               | No       | `onboarding@resend.dev`          | From address (verified domain, or Resend's onboarding address) |
| `FRONTEND_URL`              | No       | `http://localhost:8000`          | Base URL used in generated reset links |

## Database Migrations

Migrations live in `alembic/versions/` and are driven by an async Alembic
environment (`alembic/env.py`).

```bash
uv run alembic upgrade head    # apply
uv run alembic downgrade -1    # roll back one step
uv run alembic revision --autogenerate -m "description"   # new migration
```

## API Reference

All routes are prefixed `/api`. Protected routes use `Authorization: Bearer
<token>`, obtained from the token endpoint.

### Users — `/api/users`

| Method   | Path                              | Auth | Description                          |
| -------- | --------------------------------- | ---- | ------------------------------------ |
| `POST`   | `/api/users`                      | No   | Register a new user                  |
| `POST`   | `/api/users/token`                | No   | Login (OAuth2 form) → JWT            |
| `GET`    | `/api/users/me`                   | Yes  | Current user (private fields)        |
| `GET`    | `/api/users/{user_id}`            | No   | Public user profile                  |
| `PATCH`  | `/api/users/{user_id}`            | Yes  | Update username/email (owner only)   |
| `DELETE` | `/api/users/{user_id}`            | Yes  | Delete account (owner only)          |
| `PATCH`  | `/api/users/{user_id}/picture`    | Yes  | Upload / replace profile picture     |
| `DELETE` | `/api/users/{user_id}/picture`    | Yes  | Remove profile picture               |
| `PATCH`  | `/api/users/me/password`          | Yes  | Change password (requires current)   |
| `POST`   | `/api/users/forgot-password`      | No   | Send reset email (always `202`)      |
| `POST`   | `/api/users/reset-password`       | No   | Redeem reset token + new password    |
| `GET`    | `/api/users/{user_id}/posts`      | No   | Paginated posts by a user            |

> Note: `/api/users/me/password` is registered before `/api/users/{user_id}`
> in the router to avoid path collisions.

### Posts — `/api/posts`

| Method   | Path                       | Auth | Description                        |
| -------- | -------------------------- | ---- | ---------------------------------- |
| `GET`    | `/api/posts`               | No   | Paginated posts (`skip`, `limit`)  |
| `POST`   | `/api/posts`               | Yes  | Create a post                      |
| `GET`    | `/api/posts/{post_id}`     | No   | Get a single post                  |
| `PUT`    | `/api/posts/{post_id}`     | Yes  | Full update (owner only)           |
| `PATCH`  | `/api/posts/{post_id}`     | Yes  | Partial update (owner only)        |
| `DELETE` | `/api/posts/{post_id}`     | Yes  | Delete post (owner only)           |

## Pages

Server-rendered routes (not part of the JSON API):

| Route                              | Description                        |
| ---------------------------------- | ---------------------------------- |
| `/`, `/posts`                      | Home feed with "Load More"         |
| `/post/{post_id}`                  | Single post + edit/delete (owner)  |
| `/users/{user_id}/posts`           | A user's posts                     |
| `/login`, `/register`, `/account`  | Auth UI                            |
| `/forgot-password`, `/reset-password` | Password reset UI               |
| `/health`                          | Liveness/DB check                  |

## Project Structure

```
├── alembic/            # async Alembic environment + versions
├── auth.py             # JWT, password hashing, current-user dependency
├── config.py           # Pydantic settings (.env)
├── database.py         # async engine, session factory, Base
├── email_utils.py      # SMTP sending + reset email rendering
├── image_utils.py      # Pillow processing / deletion helpers
├── main.py             # FastAPI app, middleware, page routes, error handlers
├── models.py           # User, Post, PasswordResetToken
├── schemas.py          # Pydantic request/response models
├── routers/
│   ├── posts.py        # post API
│   └── users.py        # user API (auth, profile, password reset, pictures)
├── static/             # css, icons, js, default avatar
├── templates/          # Jinja2 templates (+ email/)
├── tests/              # pytest (anyio) suite
└── populate_db.py      # developer seed script (gitignored)
```

## Running Tests

The suite uses a real PostgreSQL database. By default it expects
`bloguser:blogpass@localhost/test_blog` — override the `DATABASE_URL` and
`SECRET_KEY` values at the top of `tests/conftest.py` to point elsewhere.
Tables are created and dropped per session, and each test runs inside a
rollback savepoint.

```bash
# ensure the test database exists, then:
uv run pytest
```

## Deployment

The project is designed to run anywhere a container can, backed by a managed
PostgreSQL (e.g., Neon) and a mail provider (e.g., Resend).

1. Apply migrations to the target database (`uv run alembic upgrade head`
   against that `DATABASE_URL`).
2. Build the image with `docker build -t fastapi-blog .`.
3. Push and run it on your host, injecting all variables from the
   [Environment Variables](#environment-variables) table (`--env-file .env` or
   the platform's env panel). Set `FRONTEND_URL` to the public URL so reset
   emails link correctly.
4. Note that profile images are stored on the local filesystem
   (`media/profile_pics/`). Committed seed images survive rebuilds, but user
   uploads are lost on hosts with ephemeral storage (most free tiers) — move
   image storage to the database or an object store for durable uploads.

## Contributing

Currently a personal project, but issues and pull requests are welcome — keep
the code formatted with `ruff` (`uv run ruff check .`) and add a test for any
new behavior.

## License

No license is specified for this repository.