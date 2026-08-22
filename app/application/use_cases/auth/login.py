from app.application.use_cases.auth.issue_tokens import IssueTokenPairUseCase
from app.core.exceptions import InvalidCredentialsError
from app.core.security import verify_password
from app.domain.repositories.refresh_token_repository import RefreshTokenRepository
from app.domain.repositories.user_repository import UserRepository


class LoginUseCase:
    def __init__(self, user_repository: UserRepository, refresh_token_repository: RefreshTokenRepository):
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository

    async def execute(self, email: str, password: str) -> tuple[str, str]:
        user = await self.user_repository.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Incorrect email or password")
        if not user.is_active:
            raise InvalidCredentialsError("Inactive user")

        return await IssueTokenPairUseCase(self.refresh_token_repository).execute(user.id)
