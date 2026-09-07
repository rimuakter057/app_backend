from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import PageParams, ensure_admin_or_owner, get_current_user, get_db, pagination_params, require_role
from app.crud.property import property_ as property_crud
from app.crud.visit import visit as visit_crud
from app.models.user import User
from app.models.visit import Visit
from app.schemas.common import PaginatedResponse
from app.schemas.visit import VisitCreate, VisitOut, VisitReschedule
from app.services.visit_service import cancel_visit, complete_visit, confirm_visit, create_visit, reschedule_visit

router = APIRouter(prefix="/visits", tags=["visits"])


def _get_visit_or_404(db: Session, visit_id: int) -> Visit:
    visit_obj = visit_crud.get(db, visit_id)
    if visit_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visit not found")
    return visit_obj


def _ensure_visit_owner_or_admin(db: Session, visit_obj: Visit, current_user: User) -> None:
    property_obj = property_crud.get(db, visit_obj.property_id)
    owner_id = property_obj.owner_id if property_obj is not None else None
    ensure_admin_or_owner(current_user, owner_id)


@router.post("", response_model=VisitOut, status_code=status.HTTP_201_CREATED)
def request_visit(data: VisitCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    property_obj = property_crud.get(db, data.property_id)
    if property_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    return create_visit(db, current_user, property_obj, data)


@router.get("/mine", response_model=PaginatedResponse[VisitOut])
def my_visits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page_params: PageParams = Depends(pagination_params),
):
    items = visit_crud.get_for_buyer(db, current_user.id, skip=page_params.skip, limit=page_params.page_size)
    total = visit_crud.count_for_buyer(db, current_user.id)
    return PaginatedResponse(items=items, total=total, page=page_params.page, page_size=page_params.page_size)


@router.get("/for-my-properties", response_model=PaginatedResponse[VisitOut])
def visits_for_my_properties(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("owner", "admin")),
    page_params: PageParams = Depends(pagination_params),
):
    items = visit_crud.get_for_owner(db, current_user.id, skip=page_params.skip, limit=page_params.page_size)
    total = visit_crud.count_for_owner(db, current_user.id)
    return PaginatedResponse(items=items, total=total, page=page_params.page, page_size=page_params.page_size)


@router.post("/{visit_id}/confirm", response_model=VisitOut)
def confirm(visit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    visit_obj = _get_visit_or_404(db, visit_id)
    _ensure_visit_owner_or_admin(db, visit_obj, current_user)
    return confirm_visit(db, visit_obj, current_user)


@router.post("/{visit_id}/cancel", response_model=VisitOut)
def cancel(visit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    visit_obj = _get_visit_or_404(db, visit_id)
    _ensure_visit_owner_or_admin(db, visit_obj, current_user)
    return cancel_visit(db, visit_obj, current_user)


@router.post("/{visit_id}/reschedule", response_model=VisitOut)
def reschedule(
    visit_id: int,
    data: VisitReschedule,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    visit_obj = _get_visit_or_404(db, visit_id)
    _ensure_visit_owner_or_admin(db, visit_obj, current_user)
    return reschedule_visit(db, visit_obj, data, current_user)


@router.post("/{visit_id}/complete", response_model=VisitOut)
def complete(visit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    visit_obj = _get_visit_or_404(db, visit_id)
    _ensure_visit_owner_or_admin(db, visit_obj, current_user)
    return complete_visit(db, visit_obj, current_user)
