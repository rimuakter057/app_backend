import pytest

from app.application.use_cases.auth.register import RegisterUserUseCase
from app.core.exceptions import UserAlreadyExistsError
from tests.unit.fakes import FakeUserRepository


async def test_register_new_user():
    repo = FakeUserRepository()
    use_case = RegisterUserUseCase(repo)

    user = await use_case.execute(email="test@example.com", password="secret123")

    assert user.id == 1
    assert user.email == "test@example.com"
    assert user.hashed_password != "secret123"


async def test_register_duplicate_email_raises():
    repo = FakeUserRepository()
    use_case = RegisterUserUseCase(repo)
    await use_case.execute(email="test@example.com", password="secret123")

    with pytest.raises(UserAlreadyExistsError):
        await use_case.execute(email="test@example.com", password="other")
