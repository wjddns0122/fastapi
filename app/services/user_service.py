from __future__ import annotations

from datetime import datetime
import os
import re

from sqlalchemy.orm import Session

from app.adapters.storage_client import SignedUploadData, SupabaseStorageClient
from app.core.exceptions import AppException
from app.models.user import User


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def update_profile(
        self,
        user: User,
        nickname: str | None = None,
        profile_image_url: str | None = None,
    ) -> User:
        if nickname is not None:
            user.nickname = nickname

        if profile_image_url is not None:
            user.profile_image_url = profile_image_url

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def create_profile_image_upload(
        self,
        user: User,
        file_name: str,
        content_type: str,
        storage_client: SupabaseStorageClient,
    ) -> SignedUploadData:
        if not content_type.startswith("image/"):
            raise AppException(
                code="VALIDATION_ERROR",
                message="이미지 파일만 업로드할 수 있습니다.",
                status_code=422,
            )

        normalized_file_name = self._normalize_file_name(file_name=file_name)
        file_key = self._build_profile_image_key(
            user_id=user.id,
            file_name=normalized_file_name,
        )
        return storage_client.create_signed_upload_url(
            file_key=file_key,
            content_type=content_type,
            upsert=True,
        )

    @staticmethod
    def _build_profile_image_key(user_id: str, file_name: str) -> str:
        date_prefix = datetime.now().strftime("%Y%m%d")
        return f"profiles/{user_id}/{date_prefix}-{file_name}"

    @staticmethod
    def _normalize_file_name(file_name: str) -> str:
        base_name = os.path.basename(file_name.strip())
        if not base_name:
            raise AppException(
                code="VALIDATION_ERROR",
                message="파일 이름이 올바르지 않습니다.",
                status_code=422,
            )

        sanitized_name = re.sub(r"[^A-Za-z0-9._-]", "-", base_name)
        if sanitized_name in {".", ".."}:
            raise AppException(
                code="VALIDATION_ERROR",
                message="파일 이름이 올바르지 않습니다.",
                status_code=422,
            )

        return sanitized_name
