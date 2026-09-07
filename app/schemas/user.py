from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import UserRole, VerificationStatus


class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    avatar_url: str | None = None
    company: str | None = None
    bio: str | None = None
    city: str | None = None


class UserCreate(UserBase):
    password: str = Field(min_length=8)
    role: UserRole = UserRole.buyer


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    company: str | None = None
    bio: str | None = None
    city: str | None = None


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: UserRole
    verification_status: VerificationStatus
    is_active: bool
    rating: float
    reviews_count: int
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str
