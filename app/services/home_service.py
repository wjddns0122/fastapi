from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.relationship import Relationship
from app.models.user import User
from app.services.compatibility_service import CompatibilityService
from app.services.mission_service import MissionService


class HomeService:
    def __init__(
        self,
        db: Session,
        compatibility_service: CompatibilityService,
        mission_service: MissionService,
    ) -> None:
        self.db = db
        self.compatibility_service = compatibility_service
        self.mission_service = mission_service

    def get_today_home(
        self,
        current_user: User,
        target_date: date,
        relationship_id: str | None = None,
    ) -> dict[str, object]:
        relationship = self._get_home_relationship(
            current_user=current_user,
            relationship_id=relationship_id,
        )
        compatibility = self.compatibility_service.get_today_compatibility(
            relationship_id=relationship.id,
            current_user=current_user,
            target_date=target_date,
        )
        missions = self.mission_service.list_today_missions(
            current_user=current_user,
            relationship_id=relationship.id,
            target_date=target_date,
        )
        recent_scores = self._build_recent_scores(
            relationship=relationship,
            target_date=target_date,
        )

        return {
            "relationship_id": relationship.id,
            "compatibility": compatibility,
            "keywords": self._build_keywords(
                final_score=compatibility.final_score,
                behavior_score=compatibility.behavior_score,
            ),
            "tarot_preview": {
                "card_name": compatibility.tarot_card_name,
                "card_orientation": compatibility.tarot_orientation,
                "message": compatibility.prescription,
            },
            "missions": missions,
            "letter_cta": {
                "action": "write_letter",
                "label": "오늘의 편지 쓰기",
                "suggested_prompt": "오늘 상대에게 고마웠던 순간을 짧게 남겨보세요.",
            },
            "recent_scores": recent_scores,
        }

    def _get_home_relationship(
        self,
        current_user: User,
        relationship_id: str | None,
    ) -> Relationship:
        query = self.db.query(Relationship).filter(
            Relationship.status == "accepted",
        )
        if relationship_id is not None:
            relationship = query.filter(Relationship.id == relationship_id).first()
            if relationship is None:
                raise AppException(
                    code="NOT_FOUND",
                    message="홈 화면에 사용할 관계를 찾을 수 없습니다.",
                    status_code=404,
                )
            return relationship

        relationship = (
            query.filter(
                (Relationship.requester_user_id == current_user.id)
                | (Relationship.target_user_id == current_user.id),
            )
            .order_by(Relationship.created_at.desc())
            .first()
        )
        if relationship is None:
            raise AppException(
                code="NOT_FOUND",
                message="홈 화면에 사용할 관계가 없습니다.",
                status_code=404,
            )
        return relationship

    def _build_recent_scores(
        self,
        relationship: Relationship,
        target_date: date,
    ) -> list[dict[str, object]]:
        scores: list[dict[str, object]] = []
        for offset in range(6, -1, -1):
            day = target_date - timedelta(days=offset)
            record = self.compatibility_service.ensure_daily_compatibility(
                relationship=relationship,
                target_date=day,
            )
            scores.append(
                {
                    "target_date": day,
                    "final_score": record.final_score,
                },
            )
        return scores

    @staticmethod
    def _build_keywords(final_score: int, behavior_score: int) -> list[str]:
        if final_score >= 80:
            mood_keyword = "다정함"
        elif final_score >= 60:
            mood_keyword = "대화운"
        else:
            mood_keyword = "오해주의"

        behavior_keyword = "행동상승" if behavior_score > 0 else "작은실천"
        return [mood_keyword, behavior_keyword, "관계처방"]
