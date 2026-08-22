from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.item import Item
from app.domain.repositories.item_repository import ItemRepository
from app.infrastructure.database.models.item import ItemModel


class SQLAlchemyItemRepository(ItemRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: ItemModel) -> Item:
        return Item(
            id=model.id,
            title=model.title,
            description=model.description,
            owner_id=model.owner_id,
            created_at=model.created_at,
        )

    async def get_by_id(self, item_id: int) -> Item | None:
        model = await self.session.get(ItemModel, item_id)
        return self._to_entity(model) if model else None

    async def list_by_owner(self, owner_id: int) -> list[Item]:
        result = await self.session.execute(select(ItemModel).where(ItemModel.owner_id == owner_id))
        return [self._to_entity(model) for model in result.scalars().all()]

    async def create(self, item: Item) -> Item:
        model = ItemModel(title=item.title, description=item.description, owner_id=item.owner_id)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)
