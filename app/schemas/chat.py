from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChatConversationCreate(BaseModel):
    other_user_id: int
    property_id: int | None = None


class ChatConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    property_id: int | None = None
    user_a_id: int
    user_b_id: int
    created_at: datetime


class ChatMessageCreate(BaseModel):
    text: str | None = None
    image_url: str | None = None


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    sender_id: int
    text: str | None = None
    image_url: str | None = None
    is_read: bool
    created_at: datetime
