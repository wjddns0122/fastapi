from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.daily_compatibility import DailyCompatibility
from app.models.relationship import Relationship
from app.models.user import User
from app.services.behavior_service import BehaviorService
from app.services.compatibility_engine import CompatibilityEngine
from app.services.compatibility_text_service import CompatibilityTextService


class CompatibilityService:
    def __init__(
        self,
        db: Session,
        behavior_service: BehaviorService,
        compatibility_engine: CompatibilityEngine,
        compatibility_text_service: CompatibilityTextService,
    ) -> None:
        self.db = db
        self.behavior_service = behavior_service
        self.compatibility_engine = compatibility_engine
        self.compatibility_text_service = compatibility_text_service

    def get_today_compatibility(
        self,
        relationship_id: str,
        current_user: User,
        target_date: date,
    ) -> DailyCompatibility:
        relationship = self._get_accessible_relationship(
            relationship_id=relationship_id,
            current_user=current_user,
        )
        record = self.get_by_relationship_and_date(
            relationship_id=relationship.id,
            target_date=target_date,
        )
        if record is not None:
            return record

        return self._calculate_and_save(
            relationship=relationship,
            target_date=target_date,
        )

    def refresh_today_compatibility(
        self,
        relationship_id: str,
        current_user: User,
        target_date: date,
    ) -> DailyCompatibility:
        relationship = self._get_accessible_relationship(
            relationship_id=relationship_id,
            current_user=current_user,
        )
        return self._calculate_and_save(
            relationship=relationship,
            target_date=target_date,
        )

    def get_by_relationship_and_date(
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

    def _calculate_and_save(
        self,
        relationship: Relationship,
        target_date: date,
    ) -> DailyCompatibility:
        if relationship.base_score is None:
            relationship.base_score = self.compatibility_engine.build_initial_base_score(
                requester_user_id=relationship.requester_user_id,
                target_user_id=relationship.target_user_id,
                relationship_type=relationship.relationship_type,
            )
            self.db.add(relationship)
            self.db.commit()
            self.db.refresh(relationship)

        tarot_result = self.compatibility_engine.get_tarot_result(
            relationship_id=relationship.id,
            target_date=target_date,
        )
        behavior_metrics = self.behavior_service.aggregate_recent_behavior(
            relationship=relationship,
            target_date=target_date,
        )
        behavior_score = self.compatibility_engine.score_behavior(
            behavior_metrics=behavior_metrics,
        )
        pre_adjust_score = relationship.base_score + tarot_result.score + behavior_score
        adjustment = self.compatibility_engine.get_adjustment(
            relationship_id=relationship.id,
            target_date=target_date,
            pre_adjust_score=pre_adjust_score,
        )
        final_score = self.compatibility_engine.get_final_score(
            base_score=relationship.base_score,
            tarot_score=tarot_result.score,
            behavior_score=behavior_score,
            adjustment=adjustment,
        )
        summary = self.compatibility_text_service.build_summary(
            final_score=final_score,
            tarot_result=tarot_result,
            behavior_score=behavior_score,
        )
        prescription = self.compatibility_text_service.build_prescription(
            final_score=final_score,
            tarot_result=tarot_result,
            behavior_score=behavior_score,
            behavior_metrics=behavior_metrics,
        )

        record = self.get_by_relationship_and_date(
            relationship_id=relationship.id,
            target_date=target_date,
        )
        if record is None:
            record = DailyCompatibility(
                relationship_id=relationship.id,
                target_date=target_date,
                base_score=relationship.base_score,
                tarot_score=tarot_result.score,
                behavior_score=behavior_score,
                final_score=final_score,
                summary=summary,
                prescription=prescription,
                tarot_card_name=tarot_result.card_name,
                tarot_orientation=tarot_result.orientation,
                behavior_snapshot=behavior_metrics,
            )
        else:
            record.base_score = relationship.base_score
            record.tarot_score = tarot_result.score
            record.behavior_score = behavior_score
            record.final_score = final_score
            record.summary = summary
            record.prescription = prescription
            record.tarot_card_name = tarot_result.card_name
            record.tarot_orientation = tarot_result.orientation
            record.behavior_snapshot = behavior_metrics

        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def _get_accessible_relationship(
        self,
        relationship_id: str,
        current_user: User,
    ) -> Relationship:
        relationship = self.db.query(Relationship).filter(Relationship.id == relationship_id).first()
        if relationship is None:
            raise AppException(
                code="NOT_FOUND",
                message="관계를 찾을 수 없습니다.",
                status_code=404,
            )

        is_participant = current_user.id in {
            relationship.requester_user_id,
            relationship.target_user_id,
        }
        if not is_participant:
            raise AppException(
                code="FORBIDDEN",
                message="궁합을 조회할 권한이 없습니다.",
                status_code=403,
            )

        if relationship.status != "accepted":
            raise AppException(
                code="CONFLICT",
                message="수락된 관계만 궁합을 조회할 수 있습니다.",
                status_code=409,
            )

        return relationship
