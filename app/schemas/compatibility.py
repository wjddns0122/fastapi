from datetime import date

from pydantic import ConfigDict, Field

from app.schemas.base import CamelModel


class DailyCompatibilityResponseSchema(CamelModel):
    """오늘의 궁합 응답 스키마"""

    model_config = ConfigDict(
        alias_generator=CamelModel.model_config.get("alias_generator"),
        populate_by_name=True,
        from_attributes=True,
        json_schema_extra={
            "example": {
                "relationshipId": "uuid",
                "targetDate": "2026-04-10",
                "baseScore": 62,
                "tarotScore": 10,
                "behaviorScore": 8,
                "finalScore": 80,
                "summary": "오늘은 대화 흐름이 좋고, 먼저 안부를 건네면 분위기가 더 좋아질 수 있습니다.",
                "prescription": "가벼운 칭찬 한 마디를 먼저 건네보세요.",
            },
        },
    )

    relationship_id: str = Field(examples=["uuid"])
    target_date: date = Field(examples=["2026-04-10"])
    base_score: int = Field(ge=0, le=100, examples=[62])
    tarot_score: int = Field(examples=[10])
    behavior_score: int = Field(examples=[8])
    final_score: int = Field(ge=0, le=100, examples=[80])
    summary: str = Field(
        examples=["오늘은 대화 흐름이 좋고, 먼저 안부를 건네면 분위기가 더 좋아질 수 있습니다."],
    )
    prescription: str = Field(examples=["가벼운 칭찬 한 마디를 먼저 건네보세요."])
