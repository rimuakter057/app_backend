from app.core.exceptions import UserAlreadyExistsError
from app.core.security import hash_password
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository


class RegisterUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, email: str, password: str, full_name: str | None = None) -> User:
        existing = await self.user_repository.get_by_email(email)
        if existing:
            raise UserAlreadyExistsError(f"User with email {email} already exists")

        user = User(
            id=None,
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
        )
        return await self.user_repository.create(user)
