from app.domain.entities.item import Item
from app.domain.repositories.item_repository import ItemRepository


class CreateItemUseCase:
    def __init__(self, item_repository: ItemRepository):
        self.item_repository = item_repository

    async def execute(self, title: str, description: str | None, owner_id: int) -> Item:
        item = Item(id=None, title=title, description=description, owner_id=owner_id)
        return await self.item_repository.create(item)
