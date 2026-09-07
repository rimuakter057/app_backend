import logging

from sqlalchemy.orm import Session

from app.crud.lead import lead as lead_crud
from app.models.enums import LeadStatus, NotificationKind
from app.models.lead import Lead
from app.models.property import Property
from app.models.user import User
from app.services.notification_service import notify

logger = logging.getLogger(__name__)


def get_or_create_lead(db: Session, buyer: User, property_obj: Property, message: str | None = None) -> Lead:
    existing = lead_crud.get_by_buyer_and_property(db, buyer.id, property_obj.id)
    if existing:
        return existing
    lead_obj = lead_crud.create(
        db,
        {
            "property_id": property_obj.id,
            "buyer_id": buyer.id,
            "owner_id": property_obj.owner_id,
            "message": message,
            "status": LeadStatus.new,
        },
    )
    notify(
        db,
        user_id=property_obj.owner_id,
        title="New lead",
        body=f"{buyer.name} is interested in '{property_obj.title}'.",
        kind=NotificationKind.lead,
    )
    return lead_obj


def update_lead_status(db: Session, lead_obj: Lead, new_status: LeadStatus, actor: User) -> Lead:
    lead_obj = lead_crud.update(db, db_obj=lead_obj, obj_in={"status": new_status})
    logger.info("Lead %s status changed to %s by user %s", lead_obj.id, new_status.value, actor.id)
    return lead_obj
