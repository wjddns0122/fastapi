from __future__ import annotations

import hashlib
from datetime import date

from sqlalchemy.orm import Session

from app.models.daily_compatibility import DailyCompatibility
from app.models.relationship import Relationship
from app.models.user import User
from app.services.relationship_access import ensure_relationship_access


class CompatibilityService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_today_compatibility(
        self,
        current_user: User,
        relationship_id: str,
        target_date: date,
    ) -> DailyCompatibility:
        relationship = self._get_accessible_relationship(
            current_user=current_user,
            relationship_id=relationship_id,
        )
        return self.ensure_daily_compatibility(
            relationship=relationship,
            target_date=target_date,
        )

    def refresh_today_compatibility(
        self,
        current_user: User,
        relationship_id: str,
        target_date: date,
    ) -> DailyCompatibility:
        relationship = self._get_accessible_relationship(
            current_user=current_user,
            relationship_id=relationship_id,
        )
        existing = self._get_by_relationship_and_date(
            relationship_id=relationship.id,
            target_date=target_date,
        )
        if existing is None:
            return self._create_daily_compatibility(
                relationship=relationship,
                target_date=target_date,
            )

        scores = self._calculate_scores(
            relationship_id=relationship.id,
            target_date=target_date,
            salt="refresh",
        )
        existing.base_score = scores["base_score"]
        existing.tarot_score = scores["tarot_score"]
        existing.behavior_score = scores["behavior_score"]
        existing.final_score = scores["final_score"]
        existing.summary = self._build_summary(final_score=existing.final_score)
        existing.prescription = self._build_prescription(final_score=existing.final_score)
        self.db.add(existing)
        self.db.commit()
        self.db.refresh(existing)
        return existing

    def generate_daily_for_all(self, target_date: date) -> int:
        relationships = (
            self.db.query(Relationship)
            .filter(Relationship.status == "accepted")
            .all()
        )
        generated_count = 0
        for relationship in relationships:
            existing = self._get_by_relationship_and_date(
                relationship_id=relationship.id,
                target_date=target_date,
            )
            if existing is None:
                self.ensure_daily_compatibility(
                    relationship=relationship,
                    target_date=target_date,
                )
                generated_count += 1
        return generated_count

    def ensure_daily_compatibility(
        self,
        relationship: Relationship,
        target_date: date,
    ) -> DailyCompatibility:
        """관계와 날짜 기준 궁합 레코드를 조회하거나 없으면 생성한다."""
        existing = self._get_by_relationship_and_date(
            relationship_id=relationship.id,
            target_date=target_date,
        )
        if existing is not None:
            return existing
        return self._create_daily_compatibility(
            relationship=relationship,
            target_date=target_date,
        )

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
            forbidden_message="궁합을 조회할 권한이 없습니다.",
        )

    def _get_by_relationship_and_date(
        self,
        relationship_id: str,
        target_date: date,
    ) -> DailyCompatibility | None:
        return (
            self.db.query(DailyCompatibility)
            .filter(
                DailyCompatibility.relationship_id == relationship_id,
                DailyCompatibility.target_date == target_date,
            )
            .first()
        )

    def _create_daily_compatibility(
        self,
        relationship: Relationship,
        target_date: date,
    ) -> DailyCompatibility:
        scores = self._calculate_scores(
            relationship_id=relationship.id,
            target_date=target_date,
        )
        daily_compatibility = DailyCompatibility(
            relationship_id=relationship.id,
            target_date=target_date,
            base_score=scores["base_score"],
            tarot_score=scores["tarot_score"],
            behavior_score=scores["behavior_score"],
            final_score=scores["final_score"],
            summary=self._build_summary(final_score=scores["final_score"]),
            prescription=self._build_prescription(final_score=scores["final_score"]),
        )
        self.db.add(daily_compatibility)
        self.db.commit()
        self.db.refresh(daily_compatibility)
        return daily_compatibility

    @staticmethod
    def _calculate_scores(
        relationship_id: str,
        target_date: date,
        salt: str = "default",
    ) -> dict[str, int]:
        seed_text = f"{relationship_id}:{target_date.isoformat()}:{salt}"
        seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest(), 16)
        base_score = 45 + (seed % 36)
        tarot_score = (seed // 36) % 16
        behavior_score = (seed // (36 * 16)) % 16
        final_score = min(100, base_score + tarot_score + behavior_score)
        return {
            "base_score": base_score,
            "tarot_score": tarot_score,
            "behavior_score": behavior_score,
            "final_score": final_score,
        }

    @staticmethod
    def _build_summary(final_score: int) -> str:
        if final_score >= 80:
            return "오늘은 관계 흐름이 안정적이고 대화가 잘 이어질 수 있습니다."
        if final_score >= 60:
            return "오늘은 작은 배려가 관계 분위기를 부드럽게 만들 수 있습니다."
        return "오늘은 감정이 엇갈릴 수 있어 천천히 접근하는 편이 좋습니다."

    @staticmethod
    def _build_prescription(final_score: int) -> str:
        if final_score >= 80:
            return "가벼운 칭찬이나 고마운 마음을 먼저 표현해보세요."
        if final_score >= 60:
            return "짧은 안부 메시지로 부담 없이 대화를 시작해보세요."
        return "답을 재촉하지 말고 상대가 편하게 반응할 시간을 주세요."
