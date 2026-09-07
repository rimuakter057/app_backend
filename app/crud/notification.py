from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.notification import Notification
from app.schemas.notification import NotificationOut


class CRUDNotification(CRUDBase[Notification, NotificationOut, NotificationOut]):
    def get_for_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 20) -> list[Notification]:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

    def count_for_user(self, db: Session, user_id: int) -> int:
        stmt = select(func.count()).select_from(Notification).where(Notification.user_id == user_id)
        return db.scalar(stmt) or 0

    def mark_read(self, db: Session, notification: Notification) -> Notification:
        notification.is_read = True
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification


notification = CRUDNotification(Notification)
