from datetime import datetime
from typing import Literal

from pydantic import Field

from app.schemas.base import CamelModel

LetterType = Literal["instant", "scheduled", "timecapsule"]
LetterStatus = Literal["draft", "scheduled", "sent", "canceled"]


class CreateLetterRequestSchema(CamelModel):
    """편지 작성 요청 스키마"""

    relationship_id: str = Field(examples=["uuid"])
    receiver_user_id: str = Field(examples=["uuid"])
    content: str = Field(min_length=1, max_length=2000)
    letter_type: LetterType = Field(examples=["scheduled"])
    scheduled_at: datetime | None = Field(default=None)


class LetterCreateResponseSchema(CamelModel):
    """편지 생성 응답 스키마"""

    id: str = Field(examples=["uuid"])
    status: LetterStatus = Field(examples=["scheduled"])


class LetterResponseSchema(CamelModel):
    """편지 상세 응답 스키마"""

    id: str
    relationship_id: str
    sender_user_id: str
    receiver_user_id: str
    content: str
    letter_type: LetterType
    status: LetterStatus
    scheduled_at: datetime | None = None
    sent_at: datetime | None = None
    created_at: datetime


class LetterAttachmentPresignRequestSchema(CamelModel):
    """편지 첨부 이미지 업로드 URL 요청 스키마"""

    file_name: str = Field(min_length=1, max_length=255, examples=["letter-image.jpg"])
    content_type: str = Field(min_length=1, max_length=100, examples=["image/jpeg"])


class LetterAttachmentPresignResponseSchema(CamelModel):
    """편지 첨부 이미지 업로드 URL 응답 스키마"""

    file_key: str
    upload_url: str
    public_url: str
