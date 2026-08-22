from dataclasses import dataclass
from datetime import datetime


@dataclass
class Otp:
    id: int | None
    user_id: int
    code_hash: str
    purpose: str
    expires_at: datetime
    attempts: int = 0
    is_used: bool = False
    created_at: datetime | None = None
