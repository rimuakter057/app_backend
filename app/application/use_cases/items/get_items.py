from app.domain.entities.item import Item
from app.domain.repositories.item_repository import ItemRepository


class GetItemsUseCase:
    def __init__(self, item_repository: ItemRepository):
        self.item_repository = item_repository

    async def execute(self, owner_id: int) -> list[Item]:
        return await self.item_repository.list_by_owner(owner_id)
