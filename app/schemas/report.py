from datetime import date

from pydantic import Field

from app.schemas.base import CamelModel


class WeeklyReportResponseSchema(CamelModel):
    """주간 리포트 응답 스키마"""

    relationship_id: str = Field(examples=["uuid"])
    week_start: date = Field(examples=["2026-04-06"])
    week_end: date = Field(examples=["2026-04-12"])
    average_score: int = Field(ge=0, le=100, examples=[74])
    best_day: date | None = Field(default=None)
    worst_day: date | None = Field(default=None)
    summary: str
