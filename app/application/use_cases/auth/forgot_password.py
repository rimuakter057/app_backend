from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.security import generate_otp, hash_token
from app.domain.entities.otp import Otp
from app.domain.repositories.otp_repository import OtpRepository
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.services.otp_sender import OtpSender

PASSWORD_RESET_PURPOSE = "password_reset"


class ForgotPasswordUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        otp_repository: OtpRepository,
        otp_sender: OtpSender,
    ):
        self.user_repository = user_repository
        self.otp_repository = otp_repository
        self.otp_sender = otp_sender

    async def execute(self, email: str) -> None:
        user = await self.user_repository.get_by_email(email)
        if not user:
            # Don't reveal whether the email is registered.
            return

        await self.otp_repository.invalidate_active(user.id, PASSWORD_RESET_PURPOSE)

        code = generate_otp()
        expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
            minutes=settings.OTP_EXPIRE_MINUTES
        )
        await self.otp_repository.create(
            Otp(
                id=None,
                user_id=user.id,
                code_hash=hash_token(code),
                purpose=PASSWORD_RESET_PURPOSE,
                expires_at=expires_at,
            )
        )
        await self.otp_sender.send(email=user.email, code=code)
