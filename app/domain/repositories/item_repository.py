from abc import ABC, abstractmethod

from app.domain.entities.item import Item


class ItemRepository(ABC):
    @abstractmethod
    async def get_by_id(self, item_id: int) -> Item | None: ...

    @abstractmethod
    async def list_by_owner(self, owner_id: int) -> list[Item]: ...

    @abstractmethod
    async def create(self, item: Item) -> Item: ...
