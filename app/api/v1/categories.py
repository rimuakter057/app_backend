from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.crud.category import category as category_crud
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


def _get_category_or_404(db: Session, category_id: int):
    category_obj = category_crud.get(db, category_id)
    if category_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category_obj


def _to_out(db: Session, category_obj) -> CategoryOut:
    return CategoryOut(
        id=category_obj.id,
        name=category_obj.name,
        active=category_obj.active,
        listing_count=category_crud.listing_count(db, category_obj.id),
    )


@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    categories = category_crud.get_multi(db, limit=1000)
    return [_to_out(db, c) for c in categories]


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role("admin"))])
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    return _to_out(db, category_crud.create(db, data))


@router.patch("/{category_id}", response_model=CategoryOut, dependencies=[Depends(require_role("admin"))])
def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    category_obj = _get_category_or_404(db, category_id)
    return _to_out(db, category_crud.update(db, db_obj=category_obj, obj_in=data))


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_role("admin"))])
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category_crud.delete(db, db_obj=_get_category_or_404(db, category_id))
