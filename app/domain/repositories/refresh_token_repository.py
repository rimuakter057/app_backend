from abc import ABC, abstractmethod

from app.domain.entities.refresh_token import RefreshToken


class RefreshTokenRepository(ABC):
    @abstractmethod
    async def create(self, refresh_token: RefreshToken) -> RefreshToken: ...

    @abstractmethod
    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None: ...

    @abstractmethod
    async def revoke(self, refresh_token_id: int) -> None: ...

    @abstractmethod
    async def revoke_all_for_user(self, user_id: int) -> None: ...
