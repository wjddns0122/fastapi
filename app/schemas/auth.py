from pydantic import EmailStr, Field

from app.schemas.base import CamelModel
from app.schemas.user import UserProfileSchema


class SignUpRequestSchema(CamelModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    nickname: str = Field(min_length=2, max_length=30)


class LoginRequestSchema(CamelModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class RefreshTokenRequestSchema(CamelModel):
    refresh_token: str


class AuthTokensSchema(CamelModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserWithTokensResponseSchema(CamelModel):
    user: UserProfileSchema
    tokens: AuthTokensSchema


class RefreshTokenResponseSchema(CamelModel):
    access_token: str
    token_type: str = "bearer"
