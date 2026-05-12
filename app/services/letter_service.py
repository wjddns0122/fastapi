from __future__ import annotations

from datetime import UTC, datetime
import os
import re

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.adapters.storage_client import SignedUploadData, SupabaseStorageClient
from app.core.exceptions import AppException
from app.models.letter import Letter
from app.models.relationship import Relationship
from app.models.user import User
from app.schemas.letter import LetterType
from app.services.relationship_access import ensure_relationship_access


class LetterService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_letter(
        self,
        current_user: User,
        relationship_id: str,
        receiver_user_id: str,
        content: str,
        letter_type: LetterType,
        scheduled_at: datetime | None,
    ) -> Letter:
        relationship = self._get_accessible_relationship(
            current_user=current_user,
            relationship_id=relationship_id,
        )
        if receiver_user_id not in {
            relationship.requester_user_id,
            relationship.target_user_id,
        } or receiver_user_id == current_user.id:
            raise AppException(
                code="FORBIDDEN",
                message="편지를 보낼 수 없는 사용자입니다.",
                status_code=403,
            )

        if letter_type in {"scheduled", "timecapsule"} and scheduled_at is None:
            raise AppException(
                code="VALIDATION_ERROR",
                message="예약 편지는 scheduledAt이 필요합니다.",
                status_code=422,
            )

        status = "sent" if letter_type == "instant" else "scheduled"
        sent_at = datetime.now(UTC) if letter_type == "instant" else None
        normalized_scheduled_at = None if letter_type == "instant" else scheduled_at
        letter = Letter(
            relationship_id=relationship.id,
            sender_user_id=current_user.id,
            receiver_user_id=receiver_user_id,
            content=content,
            letter_type=letter_type,
            status=status,
            scheduled_at=normalized_scheduled_at,
            sent_at=sent_at,
        )
        self.db.add(letter)
        self.db.commit()
        self.db.refresh(letter)
        return letter

    def list_letters(
        self,
        current_user: User,
        relationship_id: str | None = None,
        status: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> list[Letter]:
        query = self.db.query(Letter).filter(
            or_(
                Letter.sender_user_id == current_user.id,
                Letter.receiver_user_id == current_user.id,
            ),
        )
        if relationship_id is not None:
            self._get_accessible_relationship(
                current_user=current_user,
                relationship_id=relationship_id,
            )
            query = query.filter(Letter.relationship_id == relationship_id)
        if status is not None:
            query = query.filter(Letter.status == status)
        return (
            query.order_by(Letter.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )

    def get_letter(self, current_user: User, letter_id: str) -> Letter:
        letter = self.db.query(Letter).filter(Letter.id == letter_id).first()
        if letter is None:
            raise AppException(
                code="NOT_FOUND",
                message="편지를 찾을 수 없습니다.",
                status_code=404,
            )
        if current_user.id not in {letter.sender_user_id, letter.receiver_user_id}:
            raise AppException(
                code="FORBIDDEN",
                message="편지를 조회할 권한이 없습니다.",
                status_code=403,
            )
        return letter

    def create_attachment_upload(
        self,
        current_user: User,
        letter_id: str,
        file_name: str,
        content_type: str,
        storage_client: SupabaseStorageClient,
    ) -> SignedUploadData:
        self.get_letter(current_user=current_user, letter_id=letter_id)
        if not content_type.startswith("image/"):
            raise AppException(
                code="VALIDATION_ERROR",
                message="이미지 파일만 업로드할 수 있습니다.",
                status_code=422,
            )
        file_key = f"letters/{letter_id}/{self._normalize_file_name(file_name)}"
        return storage_client.create_signed_upload_url(
            file_key=file_key,
            content_type=content_type,
            upsert=True,
        )

    def send_scheduled_letters(self, now: datetime) -> int:
        letters = (
            self.db.query(Letter)
            .filter(
                Letter.status == "scheduled",
                Letter.scheduled_at <= now,
            )
            .all()
        )
        for letter in letters:
            letter.status = "sent"
            letter.sent_at = now
            self.db.add(letter)
        self.db.commit()
        return len(letters)

    def _get_accessible_relationship(
        self,
        current_user: User,
        relationship_id: str,
    ) -> Relationship:
        relationship = (
            self.db.query(Relationship)
            .filter(Relationship.id == relationship_id)
            .first()
        )
        return ensure_relationship_access(
            relationship=relationship,
            current_user=current_user,
            forbidden_message="편지를 작성할 권한이 없습니다.",
        )

    @staticmethod
    def _normalize_file_name(file_name: str) -> str:
        base_name = os.path.basename(file_name.strip())
        sanitized_name = re.sub(r"[^A-Za-z0-9._-]", "-", base_name)
        if not sanitized_name or sanitized_name in {".", ".."}:
            raise AppException(
                code="VALIDATION_ERROR",
                message="파일 이름이 올바르지 않습니다.",
                status_code=422,
            )
        return sanitized_name
