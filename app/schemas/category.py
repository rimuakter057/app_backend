from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    name: str
    active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = None
    active: bool | None = None


class CategoryOut(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    listing_count: int = 0
