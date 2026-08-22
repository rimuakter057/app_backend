from dataclasses import dataclass
from datetime import datetime


@dataclass
class Item:
    id: int | None
    title: str
    description: str | None
    owner_id: int
    created_at: datetime | None = None
