from datetime import date, timedelta
from typing import Any

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.crud.base import CRUDBase
from app.models.enums import PropertyStatus
from app.models.property import Property, PropertyImage
from app.models.user import User
from app.models.visit import Visit
from app.schemas.property import PropertyCreate, PropertyImageCreate, PropertyUpdate


class CRUDProperty(CRUDBase[Property, PropertyCreate, PropertyUpdate]):
    def get_with_images(self, db: Session, id: int) -> Property | None:
        stmt = select(Property).options(selectinload(Property.images)).where(Property.id == id)
        return db.scalars(stmt).first()

    def _base_query(self) -> Select:
        return select(Property).options(selectinload(Property.images)).join(
            User, User.id == Property.owner_id
        )

    def search(
        self,
        db: Session,
        *,
        q: str | None = None,
        kind: str | None = None,
        type: str | None = None,
        category_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        min_bedrooms: int | None = None,
        min_bathrooms: int | None = None,
        min_area: float | None = None,
        max_area: float | None = None,
        furnished: bool | None = None,
        city: str | None = None,
        amenities: list[str] | None = None,
        min_lat: float | None = None,
        max_lat: float | None = None,
        min_lng: float | None = None,
        max_lng: float | None = None,
        status: list[str] | None = None,
        owner_id: int | None = None,
        only_active_owners: bool = False,
        sort: str = "newest",
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Property], int]:
        stmt = self._base_query()
        conditions = []

        if q:
            like = f"%{q}%"
            conditions.append(
                or_(Property.title.ilike(like), Property.city.ilike(like), Property.address.ilike(like))
            )
        if kind:
            conditions.append(Property.kind == kind)
        if type:
            conditions.append(Property.type == type)
        if category_id is not None:
            conditions.append(Property.category_id == category_id)
        if min_price is not None:
            conditions.append(Property.price >= min_price)
        if max_price is not None:
            conditions.append(Property.price <= max_price)
        if min_bedrooms is not None:
            conditions.append(Property.bedrooms >= min_bedrooms)
        if min_bathrooms is not None:
            conditions.append(Property.bathrooms >= min_bathrooms)
        if min_area is not None:
            conditions.append(Property.area_sqft >= min_area)
        if max_area is not None:
            conditions.append(Property.area_sqft <= max_area)
        if furnished is not None:
            conditions.append(Property.furnished == furnished)
        if city:
            conditions.append(Property.city.ilike(f"%{city}%"))
        if amenities:
            conditions.append(Property.amenities.overlap(amenities))
        if min_lat is not None:
            conditions.append(Property.lat >= min_lat)
        if max_lat is not None:
            conditions.append(Property.lat <= max_lat)
        if min_lng is not None:
            conditions.append(Property.lng >= min_lng)
        if max_lng is not None:
            conditions.append(Property.lng <= max_lng)
        if status:
            conditions.append(Property.status.in_(status))
        if owner_id is not None:
            conditions.append(Property.owner_id == owner_id)
        if only_active_owners:
            conditions.append(User.is_active.is_(True))

        for condition in conditions:
            stmt = stmt.where(condition)

        count_stmt = select(func.count()).select_from(stmt.with_only_columns(Property.id).subquery())
        total = db.scalar(count_stmt) or 0

        if sort == "price_asc":
            stmt = stmt.order_by(Property.price.asc())
        elif sort == "price_desc":
            stmt = stmt.order_by(Property.price.desc())
        else:
            stmt = stmt.order_by(Property.created_at.desc())

        stmt = stmt.offset(skip).limit(limit)
        items = list(db.scalars(stmt).unique().all())
        return items, total

    def increment_views(self, db: Session, property_obj: Property) -> Property:
        property_obj.views += 1
        db.add(property_obj)
        db.commit()
        db.refresh(property_obj)
        return property_obj

    def properties_by_status_count(self, db: Session, owner_id: int) -> dict[str, int]:
        stmt = (
            select(Property.status, func.count())
            .where(Property.owner_id == owner_id)
            .group_by(Property.status)
        )
        rows = db.execute(stmt).all()
        return {status.value: count for status, count in rows}

    def total_views_for_owner(self, db: Session, owner_id: int) -> int:
        stmt = select(func.coalesce(func.sum(Property.views), 0)).where(Property.owner_id == owner_id)
        return db.scalar(stmt) or 0

    def new_listings_per_month(self, db: Session, months: int = 6) -> list[tuple[str, int]]:
        since = date.today() - timedelta(days=30 * months)
        stmt = (
            select(func.to_char(Property.created_at, "YYYY-MM"), func.count())
            .where(Property.created_at >= since)
            .group_by(func.to_char(Property.created_at, "YYYY-MM"))
            .order_by(func.to_char(Property.created_at, "YYYY-MM"))
        )
        return list(db.execute(stmt).all())

    def counts_by_status_global(self, db: Session) -> dict[str, int]:
        stmt = select(Property.status, func.count()).group_by(Property.status)
        rows = db.execute(stmt).all()
        return {status.value: count for status, count in rows}


class CRUDPropertyImage(CRUDBase[PropertyImage, PropertyImageCreate, PropertyImageCreate]):
    def get_for_property(self, db: Session, property_id: int) -> list[PropertyImage]:
        stmt = select(PropertyImage).where(PropertyImage.property_id == property_id).order_by(
            PropertyImage.sort_order
        )
        return list(db.scalars(stmt).all())


property_ = CRUDProperty(Property)
property_image = CRUDPropertyImage(PropertyImage)
