from app.application.use_cases.users.get_user import GetUserUseCase
from app.core.security import hash_password
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository


class UpdateUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(
        self, user_id: int, full_name: str | None = None, password: str | None = None
    ) -> User:
        user = await GetUserUseCase(self.user_repository).execute(user_id)

        if full_name is not None:
            user.full_name = full_name
        if password is not None:
            user.hashed_password = hash_password(password)

        return await self.user_repository.update(user)
