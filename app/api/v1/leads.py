from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import PageParams, ensure_admin_or_owner, get_current_user, get_db, pagination_params, require_role
from app.crud.lead import lead as lead_crud
from app.crud.property import property_ as property_crud
from app.models.lead import Lead
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.lead import LeadCreate, LeadOut, LeadUpdate
from app.services.lead_service import get_or_create_lead, update_lead_status

router = APIRouter(prefix="/leads", tags=["leads"])


def _get_lead_or_404(db: Session, lead_id: int) -> Lead:
    lead_obj = lead_crud.get(db, lead_id)
    if lead_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return lead_obj


@router.post("", response_model=LeadOut, status_code=status.HTTP_201_CREATED)
def contact_agent(data: LeadCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    property_obj = property_crud.get(db, data.property_id)
    if property_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    return get_or_create_lead(db, current_user, property_obj, data.message)


@router.get("/mine", response_model=PaginatedResponse[LeadOut])
def my_leads_as_buyer(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page_params: PageParams = Depends(pagination_params),
):
    items = lead_crud.get_for_buyer(db, current_user.id, skip=page_params.skip, limit=page_params.page_size)
    total = lead_crud.count_for_buyer(db, current_user.id)
    return PaginatedResponse(items=items, total=total, page=page_params.page, page_size=page_params.page_size)


@router.get("/for-my-properties", response_model=PaginatedResponse[LeadOut])
def leads_for_my_properties(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("owner", "admin")),
    page_params: PageParams = Depends(pagination_params),
):
    items = lead_crud.get_for_owner(db, current_user.id, skip=page_params.skip, limit=page_params.page_size)
    total = lead_crud.count_for_owner(db, current_user.id)
    return PaginatedResponse(items=items, total=total, page=page_params.page, page_size=page_params.page_size)


@router.patch("/{lead_id}", response_model=LeadOut)
def change_lead_status(
    lead_id: int, data: LeadUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    lead_obj = _get_lead_or_404(db, lead_id)
    ensure_admin_or_owner(current_user, lead_obj.owner_id)
    return update_lead_status(db, lead_obj, data.status, current_user)
