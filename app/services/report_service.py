from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.daily_compatibility import DailyCompatibility
from app.models.relationship import Relationship
from app.models.user import User
from app.models.weekly_report import WeeklyReport
from app.services.behavior_service import BehaviorService
from app.services.compatibility_engine import CompatibilityEngine
from app.services.compatibility_service import CompatibilityService
from app.services.compatibility_text_service import CompatibilityTextService
from app.services.relationship_access import ensure_relationship_access


class ReportService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_weekly_report(
        self,
        current_user: User,
        relationship_id: str,
        today: date,
    ) -> WeeklyReport:
        relationship = (
            self.db.query(Relationship)
            .filter(Relationship.id == relationship_id)
            .first()
        )
        relationship = ensure_relationship_access(
            relationship=relationship,
            current_user=current_user,
            forbidden_message="리포트를 조회할 권한이 없습니다.",
        )
        week_start, week_end = self._week_range(today=today)
        existing = self._get_weekly_report(
            relationship_id=relationship_id,
            week_start=week_start,
            week_end=week_end,
        )
        if existing is not None:
            return existing
        created_report = self._create_weekly_report(
            relationship_id=relationship_id,
            week_start=week_start,
            week_end=week_end,
        )
        if created_report is None:
            raise AppException(
                code="CONFLICT",
                message="주간 리포트를 생성할 데이터가 없습니다.",
                status_code=409,
            )
        return created_report

    def generate_weekly_for_all(self, today: date) -> int:
        week_start, week_end = self._week_range(today=today)
        relationships = (
            self.db.query(Relationship)
            .filter(Relationship.status == "accepted")
            .all()
        )
        generated_count = 0
        for relationship in relationships:
            existing = self._get_weekly_report(
                relationship_id=relationship.id,
                week_start=week_start,
                week_end=week_end,
            )
            if existing is None:
                created_report = self._create_weekly_report(
                    relationship_id=relationship.id,
                    week_start=week_start,
                    week_end=week_end,
                )
                if created_report is not None:
                    generated_count += 1
        return generated_count

    def get_period_report(
        self,
        current_user: User,
        relationship_id: str,
        today: date,
        period_type: str,
    ) -> dict[str, object]:
        relationship = (
            self.db.query(Relationship)
            .filter(Relationship.id == relationship_id)
            .first()
        )
        relationship = ensure_relationship_access(
            relationship=relationship,
            current_user=current_user,
            forbidden_message="리포트를 조회할 권한이 없습니다.",
        )
        period_start, period_end = self._period_range(today=today, period_type=period_type)
        records = self._list_daily_compatibilities(
            relationship_id=relationship_id,
            week_start=period_start,
            week_end=period_end,
        )
        if not records:
            compatibility_service = CompatibilityService(
                db=self.db,
                behavior_service=BehaviorService(db=self.db),
                compatibility_engine=CompatibilityEngine(),
                compatibility_text_service=CompatibilityTextService(),
            )
            records = [
                compatibility_service.ensure_daily_compatibility(
                    relationship=relationship,
                    target_date=today,
                ),
            ]

        average_score = round(sum(record.final_score for record in records) / len(records))
        best_record = max(records, key=lambda record: record.final_score)
        worst_record = min(records, key=lambda record: record.final_score)

        return {
            "relationship_id": relationship_id,
            "period_type": period_type,
            "period_start": period_start,
            "period_end": period_end,
            "average_score": average_score,
            "best_day": best_record.target_date,
            "worst_day": worst_record.target_date,
            "summary": self._build_summary(average_score=average_score),
            "highlights": self._build_highlights(
                average_score=average_score,
                record_count=len(records),
            ),
        }

    def get_premium_hub(self) -> dict[str, object]:
        return {
            "free_features": [
                "today_compatibility",
                "daily_tarot",
                "letter_write",
                "basic_missions",
                "weekly_summary",
            ],
            "paid_features": [
                "monthly_report",
                "yearly_report",
                "emotion_pattern",
                "premium_tarot_spread",
                "premium_letter_theme",
                "report_pdf_export",
            ],
            "purchase_options": [
                {"key": "premium_monthly", "label": "월 구독", "price": 4900},
                {"key": "monthly_report", "label": "월간 리포트", "price": 2900},
                {"key": "yearly_report", "label": "연간 리포트", "price": 9900},
            ],
        }

    def _create_weekly_report(
        self,
        relationship_id: str,
        week_start: date,
        week_end: date,
    ) -> WeeklyReport | None:
        compatibility_service = CompatibilityService(
            db=self.db,
            behavior_service=BehaviorService(db=self.db),
            compatibility_engine=CompatibilityEngine(),
            compatibility_text_service=CompatibilityTextService(),
        )
        relationship = (
            self.db.query(Relationship)
            .filter(Relationship.id == relationship_id)
            .first()
        )
        if relationship is None:
            return None
        records_by_date = {
            record.target_date: record
            for record in self._list_daily_compatibilities(
                relationship_id=relationship_id,
                week_start=week_start,
                week_end=week_end,
            )
        }
        current_day = week_start
        while current_day <= week_end:
            if current_day not in records_by_date:
                record = compatibility_service.ensure_daily_compatibility(
                    relationship=relationship,
                    target_date=current_day,
                )
                if record is not None:
                    records_by_date[current_day] = record
            current_day += timedelta(days=1)

        records = sorted(
            (
                record
                for record in records_by_date.values()
                if record is not None
            ),
            key=lambda record: record.target_date,
        )
        if not records:
            return None
        average_score = round(
            sum(record.final_score for record in records) / len(records),
        )
        best_record = max(records, key=lambda record: record.final_score)
        worst_record = min(records, key=lambda record: record.final_score)
        report = WeeklyReport(
            relationship_id=relationship_id,
            week_start=week_start,
            week_end=week_end,
            average_score=average_score,
            best_day=best_record.target_date,
            worst_day=worst_record.target_date,
            summary=self._build_summary(average_score=average_score),
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def _list_daily_compatibilities(
        self,
        relationship_id: str,
        week_start: date,
        week_end: date,
    ) -> list[DailyCompatibility]:
        """주간 범위에 포함되는 일별 궁합 레코드를 한 번에 조회한다."""
        return (
            self.db.query(DailyCompatibility)
            .filter(
                DailyCompatibility.relationship_id == relationship_id,
                DailyCompatibility.target_date >= week_start,
                DailyCompatibility.target_date <= week_end,
            )
            .all()
        )

    def _get_weekly_report(
        self,
        relationship_id: str,
        week_start: date,
        week_end: date,
    ) -> WeeklyReport | None:
        return (
            self.db.query(WeeklyReport)
            .filter(
                WeeklyReport.relationship_id == relationship_id,
                WeeklyReport.week_start == week_start,
                WeeklyReport.week_end == week_end,
            )
            .first()
        )

    @staticmethod
    def _week_range(today: date) -> tuple[date, date]:
        week_start = today - timedelta(days=today.weekday())
        return week_start, week_start + timedelta(days=6)

    @staticmethod
    def _period_range(today: date, period_type: str) -> tuple[date, date]:
        if period_type == "yearly":
            return date(today.year, 1, 1), date(today.year, 12, 31)

        period_start = date(today.year, today.month, 1)
        if today.month == 12:
            next_month = date(today.year + 1, 1, 1)
        else:
            next_month = date(today.year, today.month + 1, 1)
        return period_start, next_month - timedelta(days=1)

    @staticmethod
    def _build_summary(average_score: int) -> str:
        if average_score >= 80:
            return "이번 주는 관계 흐름이 전반적으로 안정적이었습니다."
        if average_score >= 60:
            return "이번 주는 작은 배려가 관계에 긍정적으로 작용했습니다."
        return "이번 주는 감정 소모를 줄이고 천천히 대화하는 편이 좋습니다."

    @staticmethod
    def _build_highlights(average_score: int, record_count: int) -> list[str]:
        if average_score >= 80:
            tone = "관계 흐름이 안정적입니다."
        elif average_score >= 60:
            tone = "작은 행동이 점수 회복에 도움이 됩니다."
        else:
            tone = "대화 속도를 늦추는 편이 좋습니다."
        return [
            tone,
            f"{record_count}일치 궁합 데이터를 반영했습니다.",
            "편지와 미션 기록이 늘어날수록 리포트 정확도가 올라갑니다.",
        ]
