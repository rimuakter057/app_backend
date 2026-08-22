from dataclasses import dataclass
from datetime import datetime


@dataclass
class RefreshToken:
    id: int | None
    user_id: int
    token_hash: str
    expires_at: datetime
    revoked: bool = False
    created_at: datetime | None = None
