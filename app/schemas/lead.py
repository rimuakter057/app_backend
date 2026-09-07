from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import LeadStatus


class LeadCreate(BaseModel):
    property_id: int
    message: str | None = None


class LeadUpdate(BaseModel):
    status: LeadStatus


class LeadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    property_id: int
    buyer_id: int
    owner_id: int
    status: LeadStatus
    message: str | None = None
    created_at: datetime
