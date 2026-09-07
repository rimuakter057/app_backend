from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.enums import ReportStatus
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportUpdate


class CRUDReport(CRUDBase[Report, ReportCreate, ReportUpdate]):
    def get_by_status(self, db: Session, status: str | None, skip: int = 0, limit: int = 20) -> list[Report]:
        stmt = select(Report).order_by(Report.created_at.desc())
        if status:
            stmt = stmt.where(Report.status == status)
        return list(db.scalars(stmt.offset(skip).limit(limit)).all())

    def count_pending(self, db: Session) -> int:
        stmt = select(func.count()).select_from(Report).where(Report.status == ReportStatus.pending)
        return db.scalar(stmt) or 0

    def count_by_status(self, db: Session, status: str | None) -> int:
        stmt = select(func.count()).select_from(Report)
        if status:
            stmt = stmt.where(Report.status == status)
        return db.scalar(stmt) or 0


report = CRUDReport(Report)
