from app.core.exceptions import InvalidResetTokenError
from app.core.security import decode_token, hash_password
from app.domain.repositories.refresh_token_repository import RefreshTokenRepository
from app.domain.repositories.user_repository import UserRepository


class ResetPasswordUseCase:
    def __init__(self, user_repository: UserRepository, refresh_token_repository: RefreshTokenRepository):
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository

    async def execute(self, reset_token: str, new_password: str) -> None:
        payload = decode_token(reset_token)
        if not payload or payload.get("type") != "password_reset":
            raise InvalidResetTokenError("Invalid or expired reset token")

        user_id = payload.get("sub")
        if user_id is None:
            raise InvalidResetTokenError("Invalid or expired reset token")

        user = await self.user_repository.get_by_id(int(user_id))
        if not user:
            raise InvalidResetTokenError("Invalid or expired reset token")

        user.hashed_password = hash_password(new_password)
        await self.user_repository.update(user)

        # Force re-login on every device after a password reset.
        await self.refresh_token_repository.revoke_all_for_user(user.id)
