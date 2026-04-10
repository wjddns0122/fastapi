from typing import Self

from pydantic import Field, model_validator

from app.schemas.base import CamelModel


class UserProfileSchema(CamelModel):
    id: str
    email: str
    nickname: str
    profile_image_url: str | None = None


class UpdateMeRequestSchema(CamelModel):
    nickname: str | None = Field(default=None, min_length=2, max_length=30)
    profile_image_url: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> Self:
        if self.nickname is None and self.profile_image_url is None:
            raise ValueError("수정할 필드를 하나 이상 입력해주세요.")
        return self


class ProfileImagePresignRequestSchema(CamelModel):
    file_name: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=100)


class ProfileImagePresignResponseSchema(CamelModel):
    file_key: str
    upload_url: str
    public_url: str
