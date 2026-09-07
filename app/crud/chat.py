from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.chat import ChatConversation, ChatMessage
from app.schemas.chat import ChatConversationCreate, ChatMessageCreate


class CRUDChatConversation(CRUDBase[ChatConversation, ChatConversationCreate, ChatConversationCreate]):
    def get_between_users(
        self, db: Session, user_a_id: int, user_b_id: int, property_id: int | None = None
    ) -> ChatConversation | None:
        stmt = select(ChatConversation).where(
            or_(
                and_(ChatConversation.user_a_id == user_a_id, ChatConversation.user_b_id == user_b_id),
                and_(ChatConversation.user_a_id == user_b_id, ChatConversation.user_b_id == user_a_id),
            )
        )
        if property_id is not None:
            stmt = stmt.where(ChatConversation.property_id == property_id)
        return db.scalars(stmt).first()

    def get_for_user(self, db: Session, user_id: int) -> list[ChatConversation]:
        stmt = select(ChatConversation).where(
            or_(ChatConversation.user_a_id == user_id, ChatConversation.user_b_id == user_id)
        ).order_by(ChatConversation.created_at.desc())
        return list(db.scalars(stmt).all())


class CRUDChatMessage(CRUDBase[ChatMessage, ChatMessageCreate, ChatMessageCreate]):
    def get_for_conversation(
        self, db: Session, conversation_id: int, skip: int = 0, limit: int = 50
    ) -> list[ChatMessage]:
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

    def count_for_conversation(self, db: Session, conversation_id: int) -> int:
        stmt = select(func.count()).select_from(ChatMessage).where(ChatMessage.conversation_id == conversation_id)
        return db.scalar(stmt) or 0

    def mark_all_read(self, db: Session, conversation_id: int, reader_id: int) -> None:
        stmt = select(ChatMessage).where(
            ChatMessage.conversation_id == conversation_id,
            ChatMessage.sender_id != reader_id,
            ChatMessage.is_read.is_(False),
        )
        for message in db.scalars(stmt).all():
            message.is_read = True
        db.commit()


chat_conversation = CRUDChatConversation(ChatConversation)
chat_message = CRUDChatMessage(ChatMessage)
