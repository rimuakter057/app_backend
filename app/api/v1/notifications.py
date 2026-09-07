from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import PageParams, get_current_user, get_db, pagination_params
from app.crud.notification import notification as notification_crud
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.notification import NotificationOut

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=PaginatedResponse[NotificationOut])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page_params: PageParams = Depends(pagination_params),
):
    items = notification_crud.get_for_user(db, current_user.id, skip=page_params.skip, limit=page_params.page_size)
    total = notification_crud.count_for_user(db, current_user.id)
    return PaginatedResponse(items=items, total=total, page=page_params.page, page_size=page_params.page_size)


@router.patch("/{notification_id}/read", response_model=NotificationOut)
def mark_notification_read(
    notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    notification_obj = notification_crud.get(db, notification_id)
    if notification_obj is None or notification_obj.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return notification_crud.mark_read(db, notification_obj)
