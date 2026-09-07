from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import PropertyKind, PropertyStatus, PropertyType

# Native Postgres array for fast "any-match" filtering (crud/property.py uses .overlap()).
# Falls back to JSON on SQLite so the test suite can create tables without Postgres.
AmenitiesType = ARRAY(String).with_variant(JSON(), "sqlite")


class Property(Base):
    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    kind: Mapped[PropertyKind] = mapped_column(
        Enum(PropertyKind, name="property_kind", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    type: Mapped[PropertyType] = mapped_column(
        Enum(PropertyType, name="property_type", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    price: Mapped[float] = mapped_column(Float, nullable=False)
    city: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    bedrooms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bathrooms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    area_sqft: Mapped[float | None] = mapped_column(Float, nullable=True)
    floor: Mapped[int | None] = mapped_column(Integer, nullable=True)
    furnished: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    property_age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    amenities: Mapped[list | None] = mapped_column(AmenitiesType, nullable=True)
    status: Mapped[PropertyStatus] = mapped_column(
        Enum(PropertyStatus, name="property_status", values_callable=lambda e: [m.value for m in e]),
        default=PropertyStatus.draft,
        nullable=False,
        index=True,
    )
    featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    images: Mapped[list["PropertyImage"]] = relationship(
        "PropertyImage", cascade="all, delete-orphan", order_by="PropertyImage.sort_order"
    )


class PropertyImage(Base):
    __tablename__ = "property_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_cover: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
