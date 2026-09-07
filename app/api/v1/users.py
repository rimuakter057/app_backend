from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import PageParams, get_db, pagination_params, require_role
from app.crud.user import user as user_crud
from app.models.enums import VerificationStatus
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.user import UserOut
from app.services.user_service import set_active, set_verification_status

router = APIRouter(prefix="/users", tags=["users"])


def _get_user_or_404(db: Session, user_id: int) -> User:
    user_obj = user_crud.get(db, user_id)
    if user_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_obj


@router.get("", response_model=PaginatedResponse[UserOut], dependencies=[Depends(require_role("admin"))])
def list_users(db: Session = Depends(get_db), page_params: PageParams = Depends(pagination_params)):
    items = user_crud.get_multi(db, skip=page_params.skip, limit=page_params.page_size)
    total = user_crud.count(db)
    return PaginatedResponse(items=items, total=total, page=page_params.page, page_size=page_params.page_size)


@router.get("/{user_id}", response_model=UserOut, dependencies=[Depends(require_role("admin"))])
def get_user(user_id: int, db: Session = Depends(get_db)):
    return _get_user_or_404(db, user_id)


@router.patch("/{user_id}/activate", response_model=UserOut, dependencies=[Depends(require_role("admin"))])
def activate_user(user_id: int, db: Session = Depends(get_db)):
    return set_active(db, _get_user_or_404(db, user_id), True)


@router.patch("/{user_id}/deactivate", response_model=UserOut, dependencies=[Depends(require_role("admin"))])
def deactivate_user(user_id: int, db: Session = Depends(get_db)):
    return set_active(db, _get_user_or_404(db, user_id), False)


@router.patch("/{user_id}/verify", response_model=UserOut, dependencies=[Depends(require_role("admin"))])
def verify_user(user_id: int, db: Session = Depends(get_db)):
    return set_verification_status(db, _get_user_or_404(db, user_id), VerificationStatus.verified)
