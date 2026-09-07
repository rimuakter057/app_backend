from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadUpdate


class CRUDLead(CRUDBase[Lead, LeadCreate, LeadUpdate]):
    def get_by_buyer_and_property(self, db: Session, buyer_id: int, property_id: int) -> Lead | None:
        stmt = select(Lead).where(Lead.buyer_id == buyer_id, Lead.property_id == property_id)
        return db.scalars(stmt).first()

    def get_for_owner(self, db: Session, owner_id: int, skip: int = 0, limit: int = 20) -> list[Lead]:
        stmt = (
            select(Lead).where(Lead.owner_id == owner_id).order_by(Lead.created_at.desc()).offset(skip).limit(limit)
        )
        return list(db.scalars(stmt).all())

    def get_for_buyer(self, db: Session, buyer_id: int, skip: int = 0, limit: int = 20) -> list[Lead]:
        stmt = (
            select(Lead).where(Lead.buyer_id == buyer_id).order_by(Lead.created_at.desc()).offset(skip).limit(limit)
        )
        return list(db.scalars(stmt).all())

    def distinct_leads_count_for_owner(self, db: Session, owner_id: int) -> int:
        stmt = select(func.count(func.distinct(Lead.buyer_id))).where(Lead.owner_id == owner_id)
        return db.scalar(stmt) or 0

    def count_for_buyer(self, db: Session, buyer_id: int) -> int:
        stmt = select(func.count()).select_from(Lead).where(Lead.buyer_id == buyer_id)
        return db.scalar(stmt) or 0

    def count_for_owner(self, db: Session, owner_id: int) -> int:
        stmt = select(func.count()).select_from(Lead).where(Lead.owner_id == owner_id)
        return db.scalar(stmt) or 0


lead = CRUDLead(Lead)
