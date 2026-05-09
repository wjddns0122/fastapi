from datetime import date

from pydantic import Field

from app.schemas.base import CamelModel


class DailyCompatibilityResponseSchema(CamelModel):
    """오늘의 궁합 응답 스키마"""

    relationship_id: str = Field(examples=["uuid"])
    target_date: date = Field(examples=["2026-04-10"])
    base_score: int = Field(ge=0, le=100, examples=[62])
    tarot_score: int = Field(ge=0, le=20, examples=[10])
    behavior_score: int = Field(ge=0, le=20, examples=[8])
    final_score: int = Field(ge=0, le=100, examples=[80])
    summary: str = Field(examples=["오늘은 대화 흐름이 안정적인 날입니다."])
    prescription: str = Field(examples=["가벼운 안부를 먼저 건네보세요."])
