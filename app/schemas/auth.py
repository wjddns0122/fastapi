from pydantic import EmailStr, Field

from app.schemas.base import CamelModel
from app.schemas.user import UserProfileSchema


class SignUpRequestSchema(CamelModel):
    """회원가입 요청 스키마"""
    email: EmailStr = Field(description="이메일 주소", examples=["user@example.com"])
    password: str = Field(min_length=8, max_length=128, description="비밀번호 (8자 이상)", examples=["StrongPassword123!"])
    nickname: str = Field(min_length=2, max_length=30, description="닉네임", examples=["jfh"])


class LoginRequestSchema(CamelModel):
    """로그인 요청 스키마"""
    email: EmailStr = Field(description="이메일 주소", examples=["user@example.com"])
    password: str = Field(min_length=8, max_length=128, description="비밀번호", examples=["StrongPassword123!"])


class RefreshTokenRequestSchema(CamelModel):
    """토큰 재발급 요청 스키마"""
    refresh_token: str = Field(description="리프레시 토큰", examples=["jwt-refresh-token"])


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
