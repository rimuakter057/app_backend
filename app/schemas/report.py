from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import ReportStatus


class ReportCreate(BaseModel):
    property_id: int
    reason: str
    details: str | None = None


class ReportUpdate(BaseModel):
    status: ReportStatus


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    property_id: int
    reporter_id: int
    reason: str
    details: str | None = None
    status: ReportStatus
    created_at: datetime
