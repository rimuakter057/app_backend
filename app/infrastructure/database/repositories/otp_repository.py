from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.otp import Otp
from app.domain.repositories.otp_repository import OtpRepository
from app.infrastructure.database.models.otp import OtpModel


class SQLAlchemyOtpRepository(OtpRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: OtpModel) -> Otp:
        return Otp(
            id=model.id,
            user_id=model.user_id,
            code_hash=model.code_hash,
            purpose=model.purpose,
            expires_at=model.expires_at,
            attempts=model.attempts,
            is_used=model.is_used,
            created_at=model.created_at,
        )

    async def create(self, otp: Otp) -> Otp:
        model = OtpModel(
            user_id=otp.user_id,
            code_hash=otp.code_hash,
            purpose=otp.purpose,
            expires_at=otp.expires_at,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_latest_active(self, user_id: int, purpose: str) -> Otp | None:
        result = await self.session.execute(
            select(OtpModel)
            .where(
                OtpModel.user_id == user_id,
                OtpModel.purpose == purpose,
                OtpModel.is_used.is_(False),
                OtpModel.expires_at > datetime.utcnow(),
            )
            .order_by(OtpModel.created_at.desc())
        )
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def increment_attempts(self, otp_id: int) -> None:
        await self.session.execute(
            update(OtpModel).where(OtpModel.id == otp_id).values(attempts=OtpModel.attempts + 1)
        )
        await self.session.commit()

    async def mark_used(self, otp_id: int) -> None:
        await self.session.execute(update(OtpModel).where(OtpModel.id == otp_id).values(is_used=True))
        await self.session.commit()

    async def invalidate_active(self, user_id: int, purpose: str) -> None:
        await self.session.execute(
            update(OtpModel)
            .where(OtpModel.user_id == user_id, OtpModel.purpose == purpose, OtpModel.is_used.is_(False))
            .values(is_used=True)
        )
        await self.session.commit()
