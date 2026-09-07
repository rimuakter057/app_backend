from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import PageParams, get_current_user, get_db, pagination_params
from app.crud.chat import chat_conversation as chat_conversation_crud
from app.crud.chat import chat_message as chat_message_crud
from app.models.chat import ChatConversation
from app.models.user import User
from app.schemas.chat import ChatConversationCreate, ChatConversationOut, ChatMessageCreate, ChatMessageOut
from app.schemas.common import PaginatedResponse
from app.services.chat_service import send_message, start_conversation

router = APIRouter(prefix="/chats", tags=["chats"])


def _get_conversation_or_404(db: Session, conversation_id: int) -> ChatConversation:
    conversation = chat_conversation_crud.get(db, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation


def _ensure_participant(conversation: ChatConversation, current_user: User) -> None:
    if current_user.id not in (conversation.user_a_id, conversation.user_b_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")


@router.get("", response_model=list[ChatConversationOut])
def list_conversations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return chat_conversation_crud.get_for_user(db, current_user.id)


@router.post("", response_model=ChatConversationOut, status_code=status.HTTP_201_CREATED)
def create_conversation(
    data: ChatConversationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return start_conversation(db, current_user, data.other_user_id, data.property_id)


@router.get("/{conversation_id}/messages", response_model=PaginatedResponse[ChatMessageOut])
def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page_params: PageParams = Depends(pagination_params),
):
    conversation = _get_conversation_or_404(db, conversation_id)
    _ensure_participant(conversation, current_user)
    chat_message_crud.mark_all_read(db, conversation_id, current_user.id)
    items = chat_message_crud.get_for_conversation(
        db, conversation_id, skip=page_params.skip, limit=page_params.page_size
    )
    total = chat_message_crud.count_for_conversation(db, conversation_id)
    return PaginatedResponse(items=items, total=total, page=page_params.page, page_size=page_params.page_size)


@router.post("/{conversation_id}/messages", response_model=ChatMessageOut, status_code=status.HTTP_201_CREATED)
def post_message(
    conversation_id: int,
    data: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = _get_conversation_or_404(db, conversation_id)
    _ensure_participant(conversation, current_user)
    return send_message(db, conversation, current_user, data.text, data.image_url)
