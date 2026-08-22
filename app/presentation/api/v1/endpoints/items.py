from fastapi import APIRouter, status

from app.application.schemas.item import ItemCreate, ItemRead
from app.application.use_cases.items.create_item import CreateItemUseCase
from app.application.use_cases.items.get_items import GetItemsUseCase
from app.presentation.api.deps import CurrentUserDep, ItemRepoDep

router = APIRouter()


@router.get("/", response_model=list[ItemRead])
async def list_items(current_user: CurrentUserDep, item_repository: ItemRepoDep):
    return await GetItemsUseCase(item_repository).execute(owner_id=current_user.id)


@router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(item_in: ItemCreate, current_user: CurrentUserDep, item_repository: ItemRepoDep):
    return await CreateItemUseCase(item_repository).execute(
        title=item_in.title, description=item_in.description, owner_id=current_user.id
    )
