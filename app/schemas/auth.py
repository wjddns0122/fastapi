from pydantic import EmailStr, Field

from app.schemas.base import CamelModel
from app.schemas.user import UserProfileSchema


class SignUpRequestSchema(CamelModel):
    email: EmailStr = Field(examples=["user@example.com"])
    password: str = Field(min_length=8, max_length=128, examples=["StrongPassword123!"])
    nickname: str = Field(min_length=2, max_length=30, examples=["jfh"])


class LoginRequestSchema(CamelModel):
    email: EmailStr = Field(examples=["user@example.com"])
    password: str = Field(min_length=8, max_length=128, examples=["StrongPassword123!"])


class RefreshTokenRequestSchema(CamelModel):
    refresh_token: str = Field(examples=["jwt-refresh-token"])


class AuthTokensSchema(CamelModel):
    access_token: str = Field(examples=["jwt-access-token"])
    refresh_token: str = Field(examples=["jwt-refresh-token"])
    token_type: str = Field(default="bearer", examples=["bearer"])


class UserWithTokensResponseSchema(CamelModel):
    user: UserProfileSchema
    tokens: AuthTokensSchema


class RefreshTokenResponseSchema(CamelModel):
    access_token: str = Field(examples=["new-access-token"])
    token_type: str = Field(default="bearer", examples=["bearer"])
