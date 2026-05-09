from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.daily_compatibility import DailyCompatibility
from app.models.relationship import Relationship
from app.models.user import User
from app.models.weekly_report import WeeklyReport
from app.services.compatibility_service import CompatibilityService
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
        ensure_relationship_access(
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
        return self._create_weekly_report(
            relationship_id=relationship_id,
            week_start=week_start,
            week_end=week_end,
        )

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
                self._create_weekly_report(
                    relationship_id=relationship.id,
                    week_start=week_start,
                    week_end=week_end,
                )
                generated_count += 1
        return generated_count

    def _create_weekly_report(
        self,
        relationship_id: str,
        week_start: date,
        week_end: date,
    ) -> WeeklyReport:
        compatibility_service = CompatibilityService(db=self.db)
        current_day = week_start
        while current_day <= week_end:
            relationship = (
                self.db.query(Relationship)
                .filter(Relationship.id == relationship_id)
                .first()
            )
            if relationship is not None:
                existing = (
                    self.db.query(DailyCompatibility)
                    .filter(
                        DailyCompatibility.relationship_id == relationship_id,
                        DailyCompatibility.target_date == current_day,
                    )
                    .first()
                )
                if existing is None:
                    compatibility_service._create_daily_compatibility(
                        relationship=relationship,
                        target_date=current_day,
                    )
            current_day += timedelta(days=1)

        records = (
            self.db.query(DailyCompatibility)
            .filter(
                DailyCompatibility.relationship_id == relationship_id,
                DailyCompatibility.target_date >= week_start,
                DailyCompatibility.target_date <= week_end,
            )
            .all()
        )
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
    def _build_summary(average_score: int) -> str:
        if average_score >= 80:
            return "이번 주는 관계 흐름이 전반적으로 안정적이었습니다."
        if average_score >= 60:
            return "이번 주는 작은 배려가 관계에 긍정적으로 작용했습니다."
        return "이번 주는 감정 소모를 줄이고 천천히 대화하는 편이 좋습니다."
