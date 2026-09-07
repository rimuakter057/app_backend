from sqlalchemy.orm import Session

from app.crud.user import user as user_crud
from app.models.enums import VerificationStatus
from app.models.user import User


def set_verification_status(db: Session, user_obj: User, status: VerificationStatus) -> User:
    return user_crud.update(db, db_obj=user_obj, obj_in={"verification_status": status})


def set_active(db: Session, user_obj: User, is_active: bool) -> User:
    return user_crud.update(db, db_obj=user_obj, obj_in={"is_active": is_active})
