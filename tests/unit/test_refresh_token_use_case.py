from datetime import datetime, timedelta

import pytest

from app.application.use_cases.auth.refresh_token import RefreshTokenUseCase
from app.core.exceptions import InvalidRefreshTokenError
from app.core.security import generate_refresh_token, hash_token
from app.domain.entities.refresh_token import RefreshToken
from app.domain.entities.user import User
from tests.unit.fakes import FakeRefreshTokenRepository, FakeUserRepository


async def test_refresh_rotates_token_and_revokes_old_one():
    user_repo, token_repo = FakeUserRepository(), FakeRefreshTokenRepository()
    user = await user_repo.create(User(id=None, email="u@example.com", hashed_password="x"))
    plain_token = generate_refresh_token()
    stored = await token_repo.create(
        RefreshToken(
            id=None,
            user_id=user.id,
            token_hash=hash_token(plain_token),
            expires_at=datetime.utcnow() + timedelta(days=1),
        )
    )

    new_access, new_refresh = await RefreshTokenUseCase(user_repo, token_repo).execute(plain_token)

    assert new_access
    assert new_refresh != plain_token
    assert token_repo.tokens[stored.id].revoked is True


async def test_refresh_with_revoked_token_raises():
    user_repo, token_repo = FakeUserRepository(), FakeRefreshTokenRepository()
    user = await user_repo.create(User(id=None, email="u@example.com", hashed_password="x"))
    plain_token = generate_refresh_token()
    await token_repo.create(
        RefreshToken(
            id=None,
            user_id=user.id,
            token_hash=hash_token(plain_token),
            expires_at=datetime.utcnow() + timedelta(days=1),
            revoked=True,
        )
    )

    with pytest.raises(InvalidRefreshTokenError):
        await RefreshTokenUseCase(user_repo, token_repo).execute(plain_token)


async def test_refresh_with_expired_token_raises():
    user_repo, token_repo = FakeUserRepository(), FakeRefreshTokenRepository()
    user = await user_repo.create(User(id=None, email="u@example.com", hashed_password="x"))
    plain_token = generate_refresh_token()
    await token_repo.create(
        RefreshToken(
            id=None,
            user_id=user.id,
            token_hash=hash_token(plain_token),
            expires_at=datetime.utcnow() - timedelta(minutes=1),
        )
    )

    with pytest.raises(InvalidRefreshTokenError):
        await RefreshTokenUseCase(user_repo, token_repo).execute(plain_token)


async def test_refresh_with_unknown_token_raises():
    user_repo, token_repo = FakeUserRepository(), FakeRefreshTokenRepository()

    with pytest.raises(InvalidRefreshTokenError):
        await RefreshTokenUseCase(user_repo, token_repo).execute("not-a-real-token")
