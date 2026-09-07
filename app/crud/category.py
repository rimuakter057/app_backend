from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.category import Category
from app.models.property import Property
from app.schemas.category import CategoryCreate, CategoryUpdate


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    def listing_count(self, db: Session, category_id: int) -> int:
        stmt = select(func.count()).select_from(Property).where(Property.category_id == category_id)
        return db.scalar(stmt) or 0


category = CRUDCategory(Category)
