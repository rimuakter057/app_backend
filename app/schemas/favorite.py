from pydantic import BaseModel, ConfigDict


class FavoriteCreate(BaseModel):
    property_id: int


class FavoriteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    property_id: int
