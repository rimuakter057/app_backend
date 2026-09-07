from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import PageParams, get_current_user, get_db, pagination_params, require_role
from app.crud.report import report as report_crud
from app.models.report import Report
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.report import ReportCreate, ReportOut
from app.services.report_service import create_report, dismiss_report, resolve_report

router = APIRouter(prefix="/reports", tags=["reports"])


def _get_report_or_404(db: Session, report_id: int) -> Report:
    report_obj = report_crud.get(db, report_id)
    if report_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report_obj


@router.post("", response_model=ReportOut, status_code=status.HTTP_201_CREATED)
def report_property(data: ReportCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_report(db, current_user, data.property_id, data.reason, data.details)


@router.get("", response_model=PaginatedResponse[ReportOut], dependencies=[Depends(require_role("admin"))])
def list_reports(
    db: Session = Depends(get_db),
    page_params: PageParams = Depends(pagination_params),
    status_filter: str | None = None,
):
    items = report_crud.get_by_status(db, status_filter, skip=page_params.skip, limit=page_params.page_size)
    total = report_crud.count_by_status(db, status_filter)
    return PaginatedResponse(items=items, total=total, page=page_params.page, page_size=page_params.page_size)


@router.post("/{report_id}/resolve", response_model=ReportOut)
def resolve(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    return resolve_report(db, _get_report_or_404(db, report_id), current_user)


@router.post("/{report_id}/dismiss", response_model=ReportOut)
def dismiss(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    return dismiss_report(db, _get_report_or_404(db, report_id), current_user)
