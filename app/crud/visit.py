from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.property import Property
from app.models.visit import Visit
from app.schemas.visit import VisitCreate, VisitReschedule


class CRUDVisit(CRUDBase[Visit, VisitCreate, VisitReschedule]):
    def get_for_buyer(self, db: Session, buyer_id: int, skip: int = 0, limit: int = 20) -> list[Visit]:
        stmt = select(Visit).where(Visit.buyer_id == buyer_id).order_by(Visit.date.desc()).offset(skip).limit(limit)
        return list(db.scalars(stmt).all())

    def get_for_owner(self, db: Session, owner_id: int, skip: int = 0, limit: int = 20) -> list[Visit]:
        stmt = (
            select(Visit)
            .join(Property, Property.id == Visit.property_id)
            .where(Property.owner_id == owner_id)
            .order_by(Visit.date.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

    def count_for_buyer(self, db: Session, buyer_id: int) -> int:
        stmt = select(func.count()).select_from(Visit).where(Visit.buyer_id == buyer_id)
        return db.scalar(stmt) or 0

    def count_for_owner(self, db: Session, owner_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(Visit)
            .join(Property, Property.id == Visit.property_id)
            .where(Property.owner_id == owner_id)
        )
        return db.scalar(stmt) or 0

    def visits_per_month(self, db: Session, owner_id: int, months: int = 6) -> list[tuple[str, int]]:
        stmt = (
            select(func.to_char(Visit.created_at, "YYYY-MM"), func.count())
            .join(Property, Property.id == Visit.property_id)
            .where(Property.owner_id == owner_id)
            .group_by(func.to_char(Visit.created_at, "YYYY-MM"))
            .order_by(func.to_char(Visit.created_at, "YYYY-MM"))
        )
        return list(db.execute(stmt).all())


visit = CRUDVisit(Visit)
