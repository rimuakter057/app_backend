from app.application.use_cases.auth.forgot_password import PASSWORD_RESET_PURPOSE
from app.core.config import settings
from app.core.exceptions import InvalidOtpError, OtpAttemptsExceededError
from app.core.security import create_password_reset_token, hash_token
from app.domain.repositories.otp_repository import OtpRepository
from app.domain.repositories.user_repository import UserRepository


class VerifyOtpUseCase:
    def __init__(self, user_repository: UserRepository, otp_repository: OtpRepository):
        self.user_repository = user_repository
        self.otp_repository = otp_repository

    async def execute(self, email: str, code: str) -> str:
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise InvalidOtpError("Invalid or expired code")

        otp = await self.otp_repository.get_latest_active(user.id, PASSWORD_RESET_PURPOSE)
        if not otp:
            raise InvalidOtpError("Invalid or expired code")

        if otp.attempts >= settings.OTP_MAX_ATTEMPTS:
            raise OtpAttemptsExceededError("Too many attempts, request a new code")

        if hash_token(code) != otp.code_hash:
            await self.otp_repository.increment_attempts(otp.id)
            raise InvalidOtpError("Invalid or expired code")

        await self.otp_repository.mark_used(otp.id)
        return create_password_reset_token(subject=str(user.id))
