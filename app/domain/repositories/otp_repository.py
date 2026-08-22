from abc import ABC, abstractmethod

from app.domain.entities.otp import Otp


class OtpRepository(ABC):
    @abstractmethod
    async def create(self, otp: Otp) -> Otp: ...

    @abstractmethod
    async def get_latest_active(self, user_id: int, purpose: str) -> Otp | None: ...

    @abstractmethod
    async def increment_attempts(self, otp_id: int) -> None: ...

    @abstractmethod
    async def mark_used(self, otp_id: int) -> None: ...

    @abstractmethod
    async def invalidate_active(self, user_id: int, purpose: str) -> None: ...
