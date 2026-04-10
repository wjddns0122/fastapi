from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.relationship import Relationship
from app.models.relationship_activity import RelationshipActivity
from app.models.user import User
from app.utils.datetime import get_seoul_today


class ActivityService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def record_relationship_activity(
        self,
        relationship_id: str,
        current_user: User,
        event_type: str,
        occurred_on: date | None,
        metadata: dict[str, object],
    ) -> RelationshipActivity:
        relationship = self.db.query(Relationship).filter(Relationship.id == relationship_id).first()
        if relationship is None:
            raise AppException(
                code="NOT_FOUND",
                message="관계를 찾을 수 없습니다.",
                status_code=404,
            )

        if current_user.id not in {relationship.requester_user_id, relationship.target_user_id}:
            raise AppException(
                code="FORBIDDEN",
                message="활동을 기록할 권한이 없습니다.",
                status_code=403,
            )

        if relationship.status != "accepted":
            raise AppException(
                code="CONFLICT",
                message="수락된 관계만 활동을 기록할 수 있습니다.",
                status_code=409,
            )

        activity = RelationshipActivity(
            relationship_id=relationship.id,
            actor_user_id=current_user.id,
            event_type=event_type,
            occurred_on=occurred_on or get_seoul_today(),
            event_metadata=metadata,
        )
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return activity
