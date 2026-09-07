from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import VisitStatus


class VisitCreate(BaseModel):
    property_id: int
    date: date
    time_slot: str
    visitor_name: str | None = None
    visitor_phone: str | None = None
    note: str | None = None


class VisitReschedule(BaseModel):
    date: date
    time_slot: str


class VisitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    property_id: int
    buyer_id: int
    date: date
    time_slot: str
    status: VisitStatus
    visitor_name: str | None = None
    visitor_phone: str | None = None
    note: str | None = None
    created_at: datetime
