from sqlalchemy.orm import Session

from app.crud.favorite import favorite as favorite_crud
from app.models.favorite import Favorite
from app.models.user import User


def add_favorite(db: Session, user: User, property_id: int) -> Favorite:
    existing = favorite_crud.get_by_user_and_property(db, user.id, property_id)
    if existing:
        return existing
    return favorite_crud.create(db, {"user_id": user.id, "property_id": property_id})


def remove_favorite(db: Session, user: User, property_id: int) -> None:
    existing = favorite_crud.get_by_user_and_property(db, user.id, property_id)
    if existing:
        favorite_crud.delete(db, db_obj=existing)
