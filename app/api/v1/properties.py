from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import (
    PageParams,
    ensure_admin_or_owner,
    get_current_user,
    get_current_user_optional,
    get_db,
    get_property_or_404,
    pagination_params,
    require_role,
)
from app.crud.property import property_ as property_crud
from app.models.enums import PropertyKind, PropertyStatus, PropertyType, SortOption
from app.models.property import Property
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.property import PropertyCreate, PropertyImageCreate, PropertyImageOut, PropertyOut, PropertyUpdate
from app.services.property_service import (
    add_images,
    create_property,
    mark_sold,
    submit_for_approval,
    update_property,
    view_property,
)
from app.utils.image_upload import save_upload_file

router = APIRouter(prefix="/properties", tags=["properties"])


def _check_range(low: float | None, high: float | None, field: str) -> None:
    if low is not None and high is not None and low > high:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"min_{field} cannot exceed max_{field}",
        )


@router.get("", response_model=PaginatedResponse[PropertyOut])
def search_properties(
    db: Session = Depends(get_db),
    page_params: PageParams = Depends(pagination_params),
    q: str | None = None,
    kind: PropertyKind | None = None,
    type: PropertyType | None = None,
    category_id: int | None = None,
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    min_bedrooms: int | None = Query(default=None, ge=0),
    min_bathrooms: int | None = Query(default=None, ge=0),
    min_area: float | None = Query(default=None, ge=0),
    max_area: float | None = Query(default=None, ge=0),
    furnished: bool | None = None,
    city: str | None = None,
    amenities: list[str] | None = None,
    min_lat: float | None = None,
    max_lat: float | None = None,
    min_lng: float | None = None,
    max_lng: float | None = None,
    sort: SortOption = SortOption.newest,
):
    """Public/buyer-facing search. Only active listings from active owners are returned."""
    _check_range(min_price, max_price, "price")
    _check_range(min_area, max_area, "area")
    _check_range(min_lat, max_lat, "lat")
    _check_range(min_lng, max_lng, "lng")

    items, total = property_crud.search(
        db,
        q=q,
        kind=kind.value if kind else None,
        type=type.value if type else None,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        min_bedrooms=min_bedrooms,
        min_bathrooms=min_bathrooms,
        min_area=min_area,
        max_area=max_area,
        furnished=furnished,
        city=city,
        amenities=amenities,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lng=min_lng,
        max_lng=max_lng,
        status=[PropertyStatus.active.value],
        only_active_owners=True,
        sort=sort.value,
        skip=page_params.skip,
        limit=page_params.page_size,
    )
    return PaginatedResponse(items=items, total=total, page=page_params.page, page_size=page_params.page_size)


@router.get("/mine", response_model=PaginatedResponse[PropertyOut])
def my_properties(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("owner", "admin")),
    page_params: PageParams = Depends(pagination_params),
):
    items, total = property_crud.search(
        db, owner_id=current_user.id, skip=page_params.skip, limit=page_params.page_size
    )
    return PaginatedResponse(items=items, total=total, page=page_params.page, page_size=page_params.page_size)


@router.get("/{property_id}", response_model=PropertyOut)
def get_property(
    property_obj: Property = Depends(get_property_or_404),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    return view_property(db, property_obj, current_user)


@router.post("", response_model=PropertyOut, status_code=status.HTTP_201_CREATED)
def create_new_property(
    data: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("owner", "admin")),
):
    return create_property(db, current_user, data)


@router.patch("/{property_id}", response_model=PropertyOut)
def update_existing_property(
    data: PropertyUpdate,
    property_obj: Property = Depends(get_property_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_admin_or_owner(current_user, property_obj.owner_id)
    return update_property(db, property_obj, data)


@router.post("/{property_id}/submit", response_model=PropertyOut)
def submit_property(
    property_obj: Property = Depends(get_property_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_admin_or_owner(current_user, property_obj.owner_id)
    return submit_for_approval(db, property_obj, current_user)


@router.post("/{property_id}/sold", response_model=PropertyOut)
def mark_property_sold(
    property_obj: Property = Depends(get_property_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_admin_or_owner(current_user, property_obj.owner_id)
    return mark_sold(db, property_obj, current_user)


@router.post("/{property_id}/images", response_model=list[PropertyImageOut])
def add_property_images(
    images: list[PropertyImageCreate],
    property_obj: Property = Depends(get_property_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_admin_or_owner(current_user, property_obj.owner_id)
    return add_images(db, property_obj, images)


@router.post("/{property_id}/images/upload", response_model=PropertyImageOut)
def upload_property_image(
    file: UploadFile,
    property_obj: Property = Depends(get_property_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_admin_or_owner(current_user, property_obj.owner_id)
    url = save_upload_file(file, subdir="properties")
    created = add_images(db, property_obj, [PropertyImageCreate(url=url)])
    return created[0]
