from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import PageParams, get_current_user, get_db, get_property_or_404, pagination_params, require_role
from app.crud.property import property_ as property_crud
from app.models.enums import PropertyStatus
from app.models.property import Property
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.property import FeaturedToggleRequest, PropertyOut, PropertyRejectRequest
from app.schemas.stats import AdminDashboardStats
from app.services.property_service import approve_property, delete_property, reject_property, toggle_featured
from app.services.stats_service import admin_dashboard_stats

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_role("admin"))])


@router.get("/dashboard", response_model=AdminDashboardStats)
def dashboard(db: Session = Depends(get_db)):
    return admin_dashboard_stats(db)


@router.get("/properties/pending", response_model=PaginatedResponse[PropertyOut])
def pending_properties(db: Session = Depends(get_db), page_params: PageParams = Depends(pagination_params)):
    items, total = property_crud.search(
        db, status=[PropertyStatus.pending.value], skip=page_params.skip, limit=page_params.page_size
    )
    return PaginatedResponse(items=items, total=total, page=page_params.page, page_size=page_params.page_size)


@router.post("/properties/{property_id}/approve", response_model=PropertyOut)
def approve(
    property_obj: Property = Depends(get_property_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return approve_property(db, property_obj, current_user)


@router.post("/properties/{property_id}/reject", response_model=PropertyOut)
def reject(
    data: PropertyRejectRequest,
    property_obj: Property = Depends(get_property_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return reject_property(db, property_obj, current_user, data.reason)


@router.patch("/properties/{property_id}/featured", response_model=PropertyOut)
def set_featured(
    data: FeaturedToggleRequest,
    property_obj: Property = Depends(get_property_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return toggle_featured(db, property_obj, data.featured, current_user)


@router.delete("/properties/{property_id}", status_code=204)
def delete(
    property_obj: Property = Depends(get_property_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_property(db, property_obj, current_user)
