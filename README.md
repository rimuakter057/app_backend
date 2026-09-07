# Real Estate API

A FastAPI + PostgreSQL backend for a real estate app: property listings, favorites, visit
scheduling, buyer-owner leads, in-app chat, notifications, and admin moderation.

## Stack

- **FastAPI** — web framework
- **PostgreSQL** + **SQLAlchemy 2.0** — database and ORM
- **Alembic** — database migrations
- **Pydantic v2** — request/response validation
- **python-jose** — JWT auth
- **passlib[bcrypt]** — password hashing

## Project layout

```
app/
  core/        # config, database session, security (JWT, password hashing, auth deps)
  models/      # SQLAlchemy ORM models (one file per entity)
  schemas/     # Pydantic request/response schemas
  crud/        # plain database access (no business rules)
  services/    # business logic (approval workflows, stats, notifications, ...)
  api/v1/      # route handlers, one router per resource
  utils/       # pagination helpers, image upload
alembic/       # migration environment and versions
tests/         # pytest test suite
```

Routes only parse the request and call into `crud`/`services` — no raw SQLAlchemy queries live in
route files, and no business rules live in `crud/base.py`.

## 1. Prerequisites

- Python 3.11+
- A running PostgreSQL instance (or Docker, see below)

## 2. Get a PostgreSQL database running

The easiest way is Docker:

```bash
docker compose up -d
```

This starts Postgres on `localhost:5432` with database `real_estate`, user `postgres`,
password `postgres` (matching `.env.example`). If you already have PostgreSQL installed
locally, just create a database named `real_estate` instead.

## 3. Set up the Python environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and adjust `DATABASE_URL` and `JWT_SECRET` if needed. The defaults match the
`docker-compose.yml` Postgres service.

## 5. Run database migrations

```bash
alembic upgrade head
```

This creates all tables. Whenever you change a model in `app/models/`, generate a new
migration with:

```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

## 6. Start the server

```bash
uvicorn app.main:app --reload
```

The API is now available at http://localhost:8000. Interactive docs (Swagger UI) are at
http://localhost:8000/docs.

## 7. Try it out

1. `POST /api/v1/auth/register` — create a buyer or owner account (`role: "buyer"` or
   `"owner"`; you cannot self-register as `"admin"` — promote a user to admin directly in
   the database for local testing).
2. `POST /api/v1/auth/login` — log in with your email/password (form fields `username`/
   `password`) to get an access + refresh token.
3. Click **Authorize** in `/docs` and paste the access token to call protected endpoints.
4. As an owner: `POST /api/v1/properties` to create a draft listing, then
   `POST /api/v1/properties/{id}/submit` to send it for approval.
5. As an admin: `GET /api/v1/admin/properties/pending` then
   `POST /api/v1/admin/properties/{id}/approve`.
6. `GET /api/v1/properties` — public search now returns the approved listing.

## Running tests

Tests run against an in-memory SQLite database (no Postgres required) and cover auth and
the core property/favorite flows:

```bash
pytest
```

## Uploaded images

Property images are saved to disk under `UPLOAD_DIR` (default `uploads/`) and served at
`/uploads/...`. This is intentionally a single function
(`app/utils/image_upload.py::save_upload_file`) so it can be swapped for S3 or another
object store later without touching any route or service code.
