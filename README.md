# FastAPI Clean Architecture

Layered FastAPI service: `domain` (entities + repository interfaces) → `application` (use cases + schemas) → `infrastructure` (SQLAlchemy models/repos) → `presentation` (API routes).

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

`.env` already ships with sane defaults (SQLite via `aiosqlite`). Change `DATABASE_URL` to a Postgres DSN (e.g. `postgresql+asyncpg://user:pass@localhost/db`) for production.

## Database migrations

```bash
alembic revision --autogenerate -m "init"
alembic upgrade head
```

## Run

```bash
uvicorn app.main:app --reload
```

API docs: http://127.0.0.1:8000/docs

## Auth flow

| Endpoint                       | Purpose                                                             |
| ------------------------------- | -------------------------------------------------------------------- |
| `POST /api/v1/auth/register`    | Sign up                                                               |
| `POST /api/v1/auth/login`       | Sign in — returns `access_token` (15 min) + `refresh_token` (30 days) |
| `POST /api/v1/auth/refresh`     | Exchange a refresh token for a new pair (old one is revoked/rotated) |
| `POST /api/v1/auth/logout`      | Revoke a refresh token                                                |
| `POST /api/v1/auth/forgot-password` | Request an OTP for password reset (always returns a generic message, never reveals if the email exists) |
| `POST /api/v1/auth/verify-otp`  | Verify the OTP, returns a short-lived `reset_token` (10 min)         |
| `POST /api/v1/auth/reset-password` | Set a new password using the `reset_token`; revokes all refresh tokens for that user |

Access tokens are JWTs (`type: access`); the reset token is also a JWT (`type: password_reset`) so it can't be reused as an access token. Refresh tokens and OTPs are opaque random values, stored only as SHA-256 hashes in the `refresh_tokens` / `otps` tables — never in plaintext.

`ConsoleOtpSender` (`app/infrastructure/services/otp_sender.py`) just prints the OTP to the console for local dev. Swap it for a real email/SMS provider by implementing `OtpSender` and wiring it in `get_otp_sender` (`app/presentation/api/deps.py`).

## Error format

Every error response — business-rule failures, request validation, auth failures, even unhandled 500s — shares the same envelope, produced by a global handler (`app/presentation/api/error_handlers.py`):

```json
{
  "error": {
    "code": "USER_ALREADY_EXISTS",
    "message": "User with email test@example.com already exists"
  }
}
```

Validation errors (422) additionally carry a `details` array (FastAPI's field-level Pydantic errors). Domain-level errors are raised as typed exceptions from `app/core/exceptions.py` (`AppError` subclasses, each with a fixed `status_code` + `code`); use cases raise them and route handlers don't need their own try/except — the handler in main.py converts them automatically. To add a new error, add an `AppError` subclass in `app/core/exceptions.py` and raise it from the use case.

## Tests

```bash
pytest
```
