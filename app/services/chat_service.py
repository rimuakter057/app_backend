from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.chat import chat_conversation as chat_conversation_crud
from app.crud.chat import chat_message as chat_message_crud
from app.crud.property import property_ as property_crud
from app.crud.user import user as user_crud
from app.models.chat import ChatConversation, ChatMessage
from app.models.enums import UserRole
from app.models.user import User
from app.services.lead_service import get_or_create_lead


def start_conversation(db: Session, current_user: User, other_user_id: int, property_id: int | None = None) -> ChatConversation:
    if other_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot start a conversation with yourself"
        )
    if user_crud.get(db, other_user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing = chat_conversation_crud.get_between_users(db, current_user.id, other_user_id, property_id)
    if existing:
        return existing

    conversation = chat_conversation_crud.create(
        db,
        {"user_a_id": current_user.id, "user_b_id": other_user_id, "property_id": property_id},
    )

    if property_id is not None and current_user.role == UserRole.buyer:
        property_obj = property_crud.get(db, property_id)
        if property_obj:
            get_or_create_lead(db, current_user, property_obj)

    return conversation


def send_message(
    db: Session, conversation: ChatConversation, sender: User, text: str | None, image_url: str | None
) -> ChatMessage:
    return chat_message_crud.create(
        db,
        {
            "conversation_id": conversation.id,
            "sender_id": sender.id,
            "text": text,
            "image_url": image_url,
        },
    )
