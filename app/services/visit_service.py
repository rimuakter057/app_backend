import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.visit import visit as visit_crud
from app.models.enums import NotificationKind, VisitStatus
from app.models.property import Property
from app.models.user import User
from app.models.visit import Visit
from app.schemas.visit import VisitCreate, VisitReschedule
from app.services.notification_service import notify

logger = logging.getLogger(__name__)


def create_visit(db: Session, buyer: User, property_obj: Property, data: VisitCreate) -> Visit:
    payload = data.model_dump(exclude={"property_id"})
    payload["buyer_id"] = buyer.id
    payload["property_id"] = property_obj.id
    payload["status"] = VisitStatus.pending
    visit_obj = visit_crud.create(db, payload)
    notify(
        db,
        user_id=property_obj.owner_id,
        title="New visit request",
        body=f"{buyer.name} requested a visit for '{property_obj.title}'.",
        kind=NotificationKind.visit,
    )
    return visit_obj


def confirm_visit(db: Session, visit_obj: Visit, actor: User) -> Visit:
    if visit_obj.status != VisitStatus.pending:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending visits can be confirmed")
    visit_obj = visit_crud.update(db, db_obj=visit_obj, obj_in={"status": VisitStatus.confirmed})
    notify(db, user_id=visit_obj.buyer_id, title="Visit confirmed", body="Your visit request was confirmed.", kind=NotificationKind.visit)
    logger.info("Visit %s confirmed by user %s", visit_obj.id, actor.id)
    return visit_obj


def cancel_visit(db: Session, visit_obj: Visit, actor: User) -> Visit:
    if visit_obj.status not in (VisitStatus.pending, VisitStatus.confirmed):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Visit cannot be cancelled")
    visit_obj = visit_crud.update(db, db_obj=visit_obj, obj_in={"status": VisitStatus.cancelled})
    notify(db, user_id=visit_obj.buyer_id, title="Visit cancelled", body="Your visit request was cancelled.", kind=NotificationKind.visit)
    logger.info("Visit %s cancelled by user %s", visit_obj.id, actor.id)
    return visit_obj


def reschedule_visit(db: Session, visit_obj: Visit, data: VisitReschedule, actor: User) -> Visit:
    if visit_obj.status not in (VisitStatus.pending, VisitStatus.confirmed):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Visit cannot be rescheduled")
    visit_obj = visit_crud.update(
        db, db_obj=visit_obj, obj_in={"date": data.date, "time_slot": data.time_slot, "status": VisitStatus.pending}
    )
    logger.info("Visit %s rescheduled by user %s", visit_obj.id, actor.id)
    return visit_obj


def complete_visit(db: Session, visit_obj: Visit, actor: User) -> Visit:
    if visit_obj.status != VisitStatus.confirmed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only confirmed visits can be completed")
    visit_obj = visit_crud.update(db, db_obj=visit_obj, obj_in={"status": VisitStatus.completed})
    logger.info("Visit %s completed by user %s", visit_obj.id, actor.id)
    return visit_obj
