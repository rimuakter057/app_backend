from datetime import datetime, timezone

from app.application.use_cases.auth.issue_tokens import IssueTokenPairUseCase
from app.core.exceptions import InvalidRefreshTokenError
from app.core.security import hash_token
from app.domain.repositories.refresh_token_repository import RefreshTokenRepository
from app.domain.repositories.user_repository import UserRepository


class RefreshTokenUseCase:
    """Validates a refresh token and rotates it: the old one is revoked and a new pair is issued."""

    def __init__(self, user_repository: UserRepository, refresh_token_repository: RefreshTokenRepository):
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository

    async def execute(self, refresh_token: str) -> tuple[str, str]:
        stored = await self.refresh_token_repository.get_by_token_hash(hash_token(refresh_token))

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        if not stored or stored.revoked or stored.expires_at < now:
            raise InvalidRefreshTokenError("Invalid or expired refresh token")

        user = await self.user_repository.get_by_id(stored.user_id)
        if not user or not user.is_active:
            raise InvalidRefreshTokenError("Invalid or expired refresh token")

        await self.refresh_token_repository.revoke(stored.id)
        return await IssueTokenPairUseCase(self.refresh_token_repository).execute(user.id)
