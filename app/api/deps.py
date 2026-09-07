from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, get_current_user_optional, require_role
from app.crud.property import property_ as property_crud
from app.models.enums import UserRole
from app.models.property import Property
from app.models.user import User
from app.utils.pagination import PageParams, pagination_params

__all__ = [
    "get_db",
    "get_current_user",
    "get_current_user_optional",
    "require_role",
    "PageParams",
    "pagination_params",
    "get_property_or_404",
    "ensure_admin_or_owner",
]


def get_property_or_404(property_id: int, db: Session = Depends(get_db)) -> Property:
    property_obj = property_crud.get_with_images(db, property_id)
    if property_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    return property_obj


def ensure_admin_or_owner(current_user: User, owner_id: int | None) -> None:
    """Allow admins through unconditionally; otherwise require current_user to be the resource owner."""
    if current_user.role == UserRole.admin:
        return
    if owner_id is None or owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
