from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.core.exceptions import InvalidTokenError
from app.core.security import decode_token
from app.domain.entities.user import User
from app.infrastructure.database.repositories.item_repository import SQLAlchemyItemRepository
from app.infrastructure.database.repositories.otp_repository import SQLAlchemyOtpRepository
from app.infrastructure.database.repositories.refresh_token_repository import (
    SQLAlchemyRefreshTokenRepository,
)
from app.infrastructure.database.repositories.user_repository import SQLAlchemyUserRepository
from app.infrastructure.services.otp_sender import ConsoleOtpSender, OtpSender

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_user_repository(session: SessionDep) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(session)


def get_item_repository(session: SessionDep) -> SQLAlchemyItemRepository:
    return SQLAlchemyItemRepository(session)


def get_refresh_token_repository(session: SessionDep) -> SQLAlchemyRefreshTokenRepository:
    return SQLAlchemyRefreshTokenRepository(session)


def get_otp_repository(session: SessionDep) -> SQLAlchemyOtpRepository:
    return SQLAlchemyOtpRepository(session)


def get_otp_sender() -> OtpSender:
    return ConsoleOtpSender()


UserRepoDep = Annotated[SQLAlchemyUserRepository, Depends(get_user_repository)]
ItemRepoDep = Annotated[SQLAlchemyItemRepository, Depends(get_item_repository)]
RefreshTokenRepoDep = Annotated[SQLAlchemyRefreshTokenRepository, Depends(get_refresh_token_repository)]
OtpRepoDep = Annotated[SQLAlchemyOtpRepository, Depends(get_otp_repository)]
OtpSenderDep = Annotated[OtpSender, Depends(get_otp_sender)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repository: UserRepoDep,
) -> User:
    credentials_exception = InvalidTokenError(
        "Could not validate credentials", headers={"WWW-Authenticate": "Bearer"}
    )

    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = await user_repository.get_by_id(int(user_id))
    if user is None:
        raise credentials_exception

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
