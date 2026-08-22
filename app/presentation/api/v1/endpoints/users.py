from fastapi import APIRouter

from app.application.schemas.user import UserRead, UserUpdate
from app.application.use_cases.users.get_user import GetUserUseCase
from app.application.use_cases.users.update_user import UpdateUserUseCase
from app.presentation.api.deps import CurrentUserDep, UserRepoDep

router = APIRouter()


@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: CurrentUserDep):
    return current_user


@router.get("/{user_id}", response_model=UserRead)
async def read_user(user_id: int, user_repository: UserRepoDep):
    return await GetUserUseCase(user_repository).execute(user_id)


@router.patch("/me", response_model=UserRead)
async def update_current_user(
    user_in: UserUpdate, current_user: CurrentUserDep, user_repository: UserRepoDep
):
    return await UpdateUserUseCase(user_repository).execute(
        user_id=current_user.id, full_name=user_in.full_name, password=user_in.password
    )
