from sqlalchemy.orm import Session

from app.crud.notification import notification as notification_crud
from app.models.enums import NotificationKind
from app.models.notification import Notification


def notify(
    db: Session, *, user_id: int, title: str, body: str | None = None, kind: NotificationKind = NotificationKind.system
) -> Notification:
    return notification_crud.create(
        db, {"user_id": user_id, "title": title, "body": body, "kind": kind}
    )
