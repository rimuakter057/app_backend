from datetime import datetime, timedelta

import pytest

from app.application.use_cases.auth.forgot_password import PASSWORD_RESET_PURPOSE
from app.application.use_cases.auth.verify_otp import VerifyOtpUseCase
from app.core.exceptions import InvalidOtpError
from app.core.security import hash_token
from app.domain.entities.otp import Otp
from app.domain.entities.user import User
from tests.unit.fakes import FakeOtpRepository, FakeUserRepository


async def _seed_user_with_otp(
    user_repo: FakeUserRepository, otp_repo: FakeOtpRepository, code: str, expires_in_minutes: int = 10
) -> User:
    user = await user_repo.create(User(id=None, email="otp@example.com", hashed_password="x"))
    await otp_repo.create(
        Otp(
            id=None,
            user_id=user.id,
            code_hash=hash_token(code),
            purpose=PASSWORD_RESET_PURPOSE,
            expires_at=datetime.utcnow() + timedelta(minutes=expires_in_minutes),
            created_at=datetime.utcnow(),
        )
    )
    return user


async def test_verify_otp_success_returns_reset_token():
    user_repo, otp_repo = FakeUserRepository(), FakeOtpRepository()
    await _seed_user_with_otp(user_repo, otp_repo, "123456")

    reset_token = await VerifyOtpUseCase(user_repo, otp_repo).execute("otp@example.com", "123456")

    assert reset_token


async def test_verify_otp_wrong_code_raises_and_counts_attempt():
    user_repo, otp_repo = FakeUserRepository(), FakeOtpRepository()
    await _seed_user_with_otp(user_repo, otp_repo, "123456")

    with pytest.raises(InvalidOtpError):
        await VerifyOtpUseCase(user_repo, otp_repo).execute("otp@example.com", "000000")

    otp = next(iter(otp_repo.otps.values()))
    assert otp.attempts == 1


async def test_verify_otp_expired_raises():
    user_repo, otp_repo = FakeUserRepository(), FakeOtpRepository()
    await _seed_user_with_otp(user_repo, otp_repo, "123456", expires_in_minutes=-1)

    with pytest.raises(InvalidOtpError):
        await VerifyOtpUseCase(user_repo, otp_repo).execute("otp@example.com", "123456")


async def test_verify_otp_unknown_email_raises():
    user_repo, otp_repo = FakeUserRepository(), FakeOtpRepository()

    with pytest.raises(InvalidOtpError):
        await VerifyOtpUseCase(user_repo, otp_repo).execute("nobody@example.com", "123456")
