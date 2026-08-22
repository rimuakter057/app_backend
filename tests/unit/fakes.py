from datetime import datetime

from app.domain.entities.otp import Otp
from app.domain.entities.refresh_token import RefreshToken
from app.domain.entities.user import User
from app.domain.repositories.otp_repository import OtpRepository
from app.domain.repositories.refresh_token_repository import RefreshTokenRepository
from app.domain.repositories.user_repository import UserRepository


class FakeUserRepository(UserRepository):
    def __init__(self):
        self.users: dict[int, User] = {}
        self._next_id = 1

    async def get_by_id(self, user_id: int) -> User | None:
        return self.users.get(user_id)

    async def get_by_email(self, email: str) -> User | None:
        return next((u for u in self.users.values() if u.email == email), None)

    async def create(self, user: User) -> User:
        user.id = self._next_id
        self.users[user.id] = user
        self._next_id += 1
        return user

    async def update(self, user: User) -> User:
        self.users[user.id] = user
        return user


class FakeRefreshTokenRepository(RefreshTokenRepository):
    def __init__(self):
        self.tokens: dict[int, RefreshToken] = {}
        self._next_id = 1

    async def create(self, refresh_token: RefreshToken) -> RefreshToken:
        refresh_token.id = self._next_id
        self.tokens[refresh_token.id] = refresh_token
        self._next_id += 1
        return refresh_token

    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        return next((t for t in self.tokens.values() if t.token_hash == token_hash), None)

    async def revoke(self, refresh_token_id: int) -> None:
        self.tokens[refresh_token_id].revoked = True

    async def revoke_all_for_user(self, user_id: int) -> None:
        for token in self.tokens.values():
            if token.user_id == user_id:
                token.revoked = True


class FakeOtpRepository(OtpRepository):
    def __init__(self):
        self.otps: dict[int, Otp] = {}
        self._next_id = 1

    async def create(self, otp: Otp) -> Otp:
        otp.id = self._next_id
        self.otps[otp.id] = otp
        self._next_id += 1
        return otp

    async def get_latest_active(self, user_id: int, purpose: str) -> Otp | None:
        candidates = [
            o
            for o in self.otps.values()
            if o.user_id == user_id
            and o.purpose == purpose
            and not o.is_used
            and o.expires_at > datetime.utcnow()
        ]
        return max(candidates, key=lambda o: o.created_at or datetime.min) if candidates else None

    async def increment_attempts(self, otp_id: int) -> None:
        self.otps[otp_id].attempts += 1

    async def mark_used(self, otp_id: int) -> None:
        self.otps[otp_id].is_used = True

    async def invalidate_active(self, user_id: int, purpose: str) -> None:
        for otp in self.otps.values():
            if otp.user_id == user_id and otp.purpose == purpose and not otp.is_used:
                otp.is_used = True
