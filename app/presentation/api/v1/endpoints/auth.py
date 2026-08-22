from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.application.schemas.auth import (
    ForgotPasswordRequest,
    GenericMessage,
    LogoutRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    TokenPair,
    VerifyOtpRequest,
    VerifyOtpResponse,
)
from app.application.schemas.user import UserCreate, UserRead
from app.application.use_cases.auth.forgot_password import ForgotPasswordUseCase
from app.application.use_cases.auth.login import LoginUseCase
from app.application.use_cases.auth.logout import LogoutUseCase
from app.application.use_cases.auth.refresh_token import RefreshTokenUseCase
from app.application.use_cases.auth.register import RegisterUserUseCase
from app.application.use_cases.auth.reset_password import ResetPasswordUseCase
from app.application.use_cases.auth.verify_otp import VerifyOtpUseCase
from app.presentation.api.deps import OtpRepoDep, OtpSenderDep, RefreshTokenRepoDep, UserRepoDep

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, user_repository: UserRepoDep):
    return await RegisterUserUseCase(user_repository).execute(
        email=user_in.email, password=user_in.password, full_name=user_in.full_name
    )


@router.post("/login", response_model=TokenPair)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_repository: UserRepoDep,
    refresh_token_repository: RefreshTokenRepoDep,
):
    access_token, refresh_token = await LoginUseCase(user_repository, refresh_token_repository).execute(
        email=form_data.username, password=form_data.password
    )
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenPair)
async def refresh(
    body: RefreshTokenRequest,
    user_repository: UserRepoDep,
    refresh_token_repository: RefreshTokenRepoDep,
):
    access_token, refresh_token = await RefreshTokenUseCase(
        user_repository, refresh_token_repository
    ).execute(body.refresh_token)
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout", response_model=GenericMessage)
async def logout(body: LogoutRequest, refresh_token_repository: RefreshTokenRepoDep):
    await LogoutUseCase(refresh_token_repository).execute(body.refresh_token)
    return GenericMessage(message="Logged out")


@router.post("/forgot-password", response_model=GenericMessage)
async def forgot_password(
    body: ForgotPasswordRequest,
    user_repository: UserRepoDep,
    otp_repository: OtpRepoDep,
    otp_sender: OtpSenderDep,
):
    await ForgotPasswordUseCase(user_repository, otp_repository, otp_sender).execute(body.email)
    return GenericMessage(message="If that email is registered, a verification code has been sent")


@router.post("/verify-otp", response_model=VerifyOtpResponse)
async def verify_otp(body: VerifyOtpRequest, user_repository: UserRepoDep, otp_repository: OtpRepoDep):
    reset_token = await VerifyOtpUseCase(user_repository, otp_repository).execute(body.email, body.code)
    return VerifyOtpResponse(reset_token=reset_token)


@router.post("/reset-password", response_model=GenericMessage)
async def reset_password(
    body: ResetPasswordRequest,
    user_repository: UserRepoDep,
    refresh_token_repository: RefreshTokenRepoDep,
):
    await ResetPasswordUseCase(user_repository, refresh_token_repository).execute(
        body.reset_token, body.new_password
    )
    return GenericMessage(message="Password has been reset")
