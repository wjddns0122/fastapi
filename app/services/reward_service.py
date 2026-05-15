from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.models.mission import MissionCompletion
from app.models.relationship import Relationship
from app.models.relationship_activity import RelationshipActivity
from app.models.user import User
from app.services.behavior_service import BehaviorService
from app.services.relationship_access import ensure_relationship_access


class RewardService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_reward_profile(
        self,
        current_user: User,
        relationship_id: str,
        today: date,
    ) -> dict[str, object]:
        relationship = (
            self.db.query(Relationship)
            .filter(Relationship.id == relationship_id)
            .first()
        )
        relationship = ensure_relationship_access(
            relationship=relationship,
            current_user=current_user,
            forbidden_message="보상 정보를 조회할 권한이 없습니다.",
        )

        mission_count = (
            self.db.query(MissionCompletion)
            .filter(MissionCompletion.relationship_id == relationship.id)
            .count()
        )
        activity_count = (
            self.db.query(RelationshipActivity)
            .filter(RelationshipActivity.relationship_id == relationship.id)
            .count()
        )
        behavior_metrics = BehaviorService(db=self.db).aggregate_recent_behavior(
            relationship=relationship,
            target_date=today,
        )
        points = mission_count * 10 + activity_count * 2
        experience = mission_count * 12 + activity_count * 3
        level = max(1, experience // 100 + 1)
        streak_days = int(behavior_metrics.get("streak_days", 0))

        badges: list[str] = []
        if mission_count > 0:
            badges.append("first_mission")
        if streak_days >= 7:
            badges.append("seven_day_streak")
        if points >= 100:
            badges.append("relationship_builder")

        return {
            "relationship_id": relationship.id,
            "points": points,
            "experience": experience,
            "level": level,
            "streak_days": streak_days,
            "badges": badges,
        }
