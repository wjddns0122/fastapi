from typing import Self

from pydantic import EmailStr, Field, model_validator

from app.schemas.base import CamelModel


class UserProfileSchema(CamelModel):
    """사용자 프로필 정보 스키마"""
    id: str = Field(description="사용자 UUID", examples=["uuid"])
    email: EmailStr = Field(description="이메일 주소", examples=["user@example.com"])
    nickname: str = Field(description="닉네임", examples=["jfh"])
    profile_image_url: str | None = Field(default=None, description="프로필 이미지 URL", examples=["https://cdn.example.com/profiles/1.png"])


class UpdateMeRequestSchema(CamelModel):
    """내 정보 수정 요청 스키마"""
    nickname: str | None = Field(default=None, min_length=2, max_length=30, description="새로운 닉네임", examples=["new_nickname"])
    profile_image_url: str | None = Field(default=None, max_length=500, description="새로운 프로필 이미지 URL", examples=["https://cdn.example.com/profiles/new.png"])

    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> Self:
        if self.nickname is None and self.profile_image_url is None:
            raise ValueError("수정할 필드를 하나 이상 입력해주세요.")
        return self


class ProfileImagePresignRequestSchema(CamelModel):
    """프로필 이미지 업로드 URL 발급 요청 스키마"""
    file_name: str = Field(min_length=1, max_length=255, description="파일명", examples=["profile.png"])
    content_type: str = Field(min_length=1, max_length=100, description="파일 타입 (MIME type)", examples=["image/png"])


class ProfileImagePresignResponseSchema(CamelModel):
    file_key: str = Field(examples=["profiles/user-uuid/20260410-profile.png"])
    upload_url: str = Field(examples=["https://s3-presigned-url"])
    public_url: str = Field(examples=["https://cdn.example.com/profiles/user-uuid/20260410-profile.png"])
