from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import PageParams, get_current_user, get_db, pagination_params
from app.crud.favorite import favorite as favorite_crud
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.property import PropertyOut
from app.services.favorite_service import add_favorite, remove_favorite

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("", response_model=PaginatedResponse[PropertyOut])
def list_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page_params: PageParams = Depends(pagination_params),
):
    favorites = favorite_crud.get_for_user(db, current_user.id, skip=page_params.skip, limit=page_params.page_size)
    total = favorite_crud.count_for_user(db, current_user.id)
    items = [f.property for f in favorites]
    return PaginatedResponse(items=items, total=total, page=page_params.page, page_size=page_params.page_size)


@router.post("/{property_id}", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def favorite_property(property_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    add_favorite(db, current_user, property_id)
    return MessageResponse(message="Added to favorites")


@router.delete("/{property_id}", response_model=MessageResponse)
def unfavorite_property(
    property_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    remove_favorite(db, current_user, property_id)
    return MessageResponse(message="Removed from favorites")
