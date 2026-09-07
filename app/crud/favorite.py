from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.crud.base import CRUDBase
from app.models.favorite import Favorite
from app.models.property import Property
from app.schemas.favorite import FavoriteCreate


class CRUDFavorite(CRUDBase[Favorite, FavoriteCreate, FavoriteCreate]):
    def get_by_user_and_property(self, db: Session, user_id: int, property_id: int) -> Favorite | None:
        stmt = select(Favorite).where(Favorite.user_id == user_id, Favorite.property_id == property_id)
        return db.scalars(stmt).first()

    def get_for_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 20) -> list[Favorite]:
        stmt = (
            select(Favorite)
            .options(selectinload(Favorite.property).selectinload(Property.images))
            .where(Favorite.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

    def count_for_user(self, db: Session, user_id: int) -> int:
        stmt = select(func.count()).select_from(Favorite).where(Favorite.user_id == user_id)
        return db.scalar(stmt) or 0


favorite = CRUDFavorite(Favorite)
