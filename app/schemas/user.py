from typing import Self

from pydantic import EmailStr, Field, model_validator

from app.schemas.base import CamelModel


class UserProfileSchema(CamelModel):
    id: str = Field(examples=["uuid"])
    email: EmailStr = Field(examples=["user@example.com"])
    nickname: str = Field(examples=["jfh"])
    profile_image_url: str | None = Field(default=None, examples=["https://cdn.example.com/profiles/1.png"])


class UpdateMeRequestSchema(CamelModel):
    nickname: str | None = Field(default=None, min_length=2, max_length=30, examples=["new_nickname"])
    profile_image_url: str | None = Field(default=None, max_length=500, examples=["https://cdn.example.com/profiles/new.png"])

    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> Self:
        if self.nickname is None and self.profile_image_url is None:
            raise ValueError("수정할 필드를 하나 이상 입력해주세요.")
        return self


class ProfileImagePresignRequestSchema(CamelModel):
    file_name: str = Field(min_length=1, max_length=255, examples=["profile.png"])
    content_type: str = Field(min_length=1, max_length=100, examples=["image/png"])


class ProfileImagePresignResponseSchema(CamelModel):
    file_key: str = Field(examples=["profiles/user-uuid/20260410-profile.png"])
    upload_url: str = Field(examples=["https://s3-presigned-url"])
    public_url: str = Field(examples=["https://cdn.example.com/profiles/user-uuid/20260410-profile.png"])
