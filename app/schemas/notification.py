from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import NotificationKind


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    body: str | None = None
    kind: NotificationKind
    is_read: bool
    created_at: datetime
