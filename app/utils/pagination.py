from fastapi import Query
from pydantic import BaseModel

from app.core.config import settings


class PageParams(BaseModel):
    page: int
    page_size: int

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.page_size


def pagination_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
) -> PageParams:
    return PageParams(page=page, page_size=page_size)
