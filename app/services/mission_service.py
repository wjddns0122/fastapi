from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.mission import MissionCompletion
from app.models.relationship import Relationship
from app.models.user import User
from app.services.relationship_access import ensure_relationship_access


class MissionService:
    _TODAY_MISSIONS: tuple[dict[str, object], ...] = (
        {
            "mission_id": "daily-compliment",
            "title": "상대 장점 1개 적기",
            "description": "오늘 상대의 좋은 점을 하나 적어보세요.",
            "reward_type": "points",
            "reward_value": 10,
        },
        {
            "mission_id": "daily-check-in",
            "title": "짧은 안부 전하기",
            "description": "부담 없는 한 문장으로 안부를 전해보세요.",
            "reward_type": "points",
            "reward_value": 10,
        },
    )

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_today_missions(
        self,
        current_user: User,
        target_date: date,
    ) -> list[dict[str, object]]:
        completions = (
            self.db.query(MissionCompletion)
            .filter(
                MissionCompletion.user_id == current_user.id,
                MissionCompletion.target_date == target_date,
            )
            .all()
        )
        completed_ids = {completion.mission_id for completion in completions}
        return [
            {
                **mission,
                "status": (
                    "completed"
                    if mission["mission_id"] in completed_ids
                    else "pending"
                ),
            }
            for mission in self._TODAY_MISSIONS
        ]

    def complete_mission(
        self,
        current_user: User,
        mission_id: str,
        relationship_id: str,
        target_date: date,
    ) -> MissionCompletion:
        if mission_id not in {str(mission["mission_id"]) for mission in self._TODAY_MISSIONS}:
            raise AppException(
                code="NOT_FOUND",
                message="미션을 찾을 수 없습니다.",
                status_code=404,
            )
        relationship = (
            self.db.query(Relationship)
            .filter(Relationship.id == relationship_id)
            .first()
        )
        ensure_relationship_access(
            relationship=relationship,
            current_user=current_user,
            forbidden_message="미션을 완료할 권한이 없습니다.",
        )
        existing = (
            self.db.query(MissionCompletion)
            .filter(
                MissionCompletion.mission_id == mission_id,
                MissionCompletion.relationship_id == relationship_id,
                MissionCompletion.user_id == current_user.id,
                MissionCompletion.target_date == target_date,
            )
            .first()
        )
        if existing is not None:
            return existing

        completion = MissionCompletion(
            mission_id=mission_id,
            relationship_id=relationship_id,
            user_id=current_user.id,
            target_date=target_date,
        )
        self.db.add(completion)
        self.db.commit()
        self.db.refresh(completion)
        return completion
