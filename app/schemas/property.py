from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import PropertyKind, PropertyStatus, PropertyType


class PropertyImageBase(BaseModel):
    url: str
    sort_order: int = 0
    is_cover: bool = False


class PropertyImageCreate(PropertyImageBase):
    pass


class PropertyImageOut(PropertyImageBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    property_id: int


class PropertyBase(BaseModel):
    title: str
    description: str | None = None
    kind: PropertyKind
    type: PropertyType
    price: float
    city: str
    address: str | None = None
    lat: float | None = None
    lng: float | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None
    area_sqft: float | None = None
    floor: int | None = None
    furnished: bool = False
    property_age: int | None = None
    amenities: list[str] | None = None
    category_id: int | None = None


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    kind: PropertyKind | None = None
    type: PropertyType | None = None
    price: float | None = None
    city: str | None = None
    address: str | None = None
    lat: float | None = None
    lng: float | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None
    area_sqft: float | None = None
    floor: int | None = None
    furnished: bool | None = None
    property_age: int | None = None
    amenities: list[str] | None = None
    category_id: int | None = None


class PropertyOut(PropertyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    status: PropertyStatus
    featured: bool
    views: int
    created_at: datetime
    updated_at: datetime
    images: list[PropertyImageOut] = []


class PropertyRejectRequest(BaseModel):
    reason: str | None = None


class FeaturedToggleRequest(BaseModel):
    featured: bool
