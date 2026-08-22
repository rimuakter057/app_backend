from typing import ClassVar

from fastapi import status


class AppError(Exception):
    """Base class for expected, user-facing application errors.

    Subclasses declare `status_code` and `code`; the global handler in
    `app.presentation.api.error_handlers` turns any raised AppError into a
    structured JSON response: {"error": {"code": ..., "message": ...}}.
    """

    status_code: ClassVar[int] = status.HTTP_400_BAD_REQUEST
    code: ClassVar[str] = "ERROR"

    def __init__(self, message: str, headers: dict[str, str] | None = None):
        self.message = message
        self.headers = headers
        super().__init__(message)


class UserAlreadyExistsError(AppError):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "USER_ALREADY_EXISTS"


class InvalidCredentialsError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "INVALID_CREDENTIALS"


class UserNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "USER_NOT_FOUND"


class InvalidTokenError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "INVALID_TOKEN"


class InvalidRefreshTokenError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "INVALID_REFRESH_TOKEN"


class InvalidOtpError(AppError):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "INVALID_OTP"


class OtpAttemptsExceededError(AppError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    code = "OTP_ATTEMPTS_EXCEEDED"


class InvalidResetTokenError(AppError):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "INVALID_RESET_TOKEN"
