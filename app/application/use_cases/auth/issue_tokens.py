from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.security import create_access_token, generate_refresh_token, hash_token
from app.domain.entities.refresh_token import RefreshToken
from app.domain.repositories.refresh_token_repository import RefreshTokenRepository


class IssueTokenPairUseCase:
    """Creates a new access token and persists a matching (hashed) refresh token."""

    def __init__(self, refresh_token_repository: RefreshTokenRepository):
        self.refresh_token_repository = refresh_token_repository

    async def execute(self, user_id: int) -> tuple[str, str]:
        access_token = create_access_token(subject=str(user_id))

        plain_refresh_token = generate_refresh_token()
        expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        await self.refresh_token_repository.create(
            RefreshToken(
                id=None,
                user_id=user_id,
                token_hash=hash_token(plain_refresh_token),
                expires_at=expires_at,
            )
        )

        return access_token, plain_refresh_token
