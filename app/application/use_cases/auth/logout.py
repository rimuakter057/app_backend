from app.core.security import hash_token
from app.domain.repositories.refresh_token_repository import RefreshTokenRepository


class LogoutUseCase:
    def __init__(self, refresh_token_repository: RefreshTokenRepository):
        self.refresh_token_repository = refresh_token_repository

    async def execute(self, refresh_token: str) -> None:
        stored = await self.refresh_token_repository.get_by_token_hash(hash_token(refresh_token))
        if stored and not stored.revoked:
            await self.refresh_token_repository.revoke(stored.id)
