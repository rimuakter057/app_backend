import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.property import property_ as property_crud
from app.crud.property import property_image as property_image_crud
from app.models.enums import NotificationKind, PropertyStatus
from app.models.property import Property
from app.models.user import User
from app.schemas.property import PropertyCreate, PropertyImageCreate, PropertyUpdate
from app.services.notification_service import notify

logger = logging.getLogger(__name__)


def create_property(db: Session, owner: User, data: PropertyCreate) -> Property:
    payload = data.model_dump()
    payload["owner_id"] = owner.id
    payload["status"] = PropertyStatus.draft
    return property_crud.create(db, payload)


def update_property(db: Session, property_obj: Property, data: PropertyUpdate) -> Property:
    return property_crud.update(db, db_obj=property_obj, obj_in=data)


def submit_for_approval(db: Session, property_obj: Property, actor: User) -> Property:
    if property_obj.status != PropertyStatus.draft:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft properties can be submitted for approval",
        )
    property_obj = property_crud.update(db, db_obj=property_obj, obj_in={"status": PropertyStatus.pending})
    logger.info("Property %s submitted for approval by user %s", property_obj.id, actor.id)
    return property_obj


def approve_property(db: Session, property_obj: Property, actor: User) -> Property:
    if property_obj.status != PropertyStatus.pending:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending properties can be approved")
    property_obj = property_crud.update(db, db_obj=property_obj, obj_in={"status": PropertyStatus.active})
    notify(
        db,
        user_id=property_obj.owner_id,
        title="Listing approved",
        body=f"Your listing '{property_obj.title}' is now live.",
        kind=NotificationKind.approval,
    )
    logger.info("Property %s approved by user %s", property_obj.id, actor.id)
    return property_obj


def reject_property(db: Session, property_obj: Property, actor: User, reason: str | None = None) -> Property:
    if property_obj.status != PropertyStatus.pending:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending properties can be rejected")
    property_obj = property_crud.update(db, db_obj=property_obj, obj_in={"status": PropertyStatus.rejected})
    body = f"Your listing '{property_obj.title}' was rejected."
    if reason:
        body += f" Reason: {reason}"
    notify(db, user_id=property_obj.owner_id, title="Listing rejected", body=body, kind=NotificationKind.approval)
    logger.info("Property %s rejected by user %s", property_obj.id, actor.id)
    return property_obj


def mark_sold(db: Session, property_obj: Property, actor: User) -> Property:
    if property_obj.status != PropertyStatus.active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only active properties can be marked sold")
    property_obj = property_crud.update(db, db_obj=property_obj, obj_in={"status": PropertyStatus.sold})
    logger.info("Property %s marked sold by user %s", property_obj.id, actor.id)
    return property_obj


def toggle_featured(db: Session, property_obj: Property, featured: bool, actor: User) -> Property:
    if property_obj.status != PropertyStatus.active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Only active properties can be featured"
        )
    property_obj = property_crud.update(db, db_obj=property_obj, obj_in={"featured": featured})
    logger.info("Property %s featured=%s set by user %s", property_obj.id, featured, actor.id)
    return property_obj


def delete_property(db: Session, property_obj: Property, actor: User) -> None:
    logger.info("Property %s deleted by user %s", property_obj.id, actor.id)
    property_crud.delete(db, db_obj=property_obj)


def add_images(db: Session, property_obj: Property, images: list[PropertyImageCreate]) -> list:
    created = []
    for image in images:
        payload = image.model_dump()
        payload["property_id"] = property_obj.id
        created.append(property_image_crud.create(db, payload))
    return created


def view_property(db: Session, property_obj: Property, viewer: User | None) -> Property:
    """Return property detail, incrementing the view counter for non-owner viewers."""
    if viewer is None or viewer.id != property_obj.owner_id:
        property_obj = property_crud.increment_views(db, property_obj)
    return property_obj
