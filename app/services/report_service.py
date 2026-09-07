import logging

from sqlalchemy.orm import Session

from app.crud.report import report as report_crud
from app.models.enums import ReportStatus
from app.models.report import Report
from app.models.user import User

logger = logging.getLogger(__name__)


def create_report(db: Session, reporter: User, property_id: int, reason: str, details: str | None = None) -> Report:
    return report_crud.create(
        db,
        {
            "property_id": property_id,
            "reporter_id": reporter.id,
            "reason": reason,
            "details": details,
            "status": ReportStatus.pending,
        },
    )


def resolve_report(db: Session, report_obj: Report, actor: User) -> Report:
    report_obj = report_crud.update(db, db_obj=report_obj, obj_in={"status": ReportStatus.resolved})
    logger.info("Report %s resolved by user %s", report_obj.id, actor.id)
    return report_obj


def dismiss_report(db: Session, report_obj: Report, actor: User) -> Report:
    report_obj = report_crud.update(db, db_obj=report_obj, obj_in={"status": ReportStatus.dismissed})
    logger.info("Report %s dismissed by user %s", report_obj.id, actor.id)
    return report_obj
