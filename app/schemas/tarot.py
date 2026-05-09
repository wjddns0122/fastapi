from datetime import date

from pydantic import ConfigDict, Field

from app.schemas.base import CamelModel


class CreateDailyTarotRequestSchema(CamelModel):
    model_config = ConfigDict(
        alias_generator=CamelModel.model_config.get("alias_generator"),
        populate_by_name=True,
        from_attributes=True,
        json_schema_extra={
            "example": {
                "relationshipId": "uuid",
                "question": "오늘 상대에게 먼저 연락해도 될까?",
            },
        },
    )

    relationship_id: str = Field(examples=["uuid"])
    question: str = Field(
        min_length=2,
        max_length=200,
        examples=["오늘 상대에게 먼저 연락해도 될까?"],
    )


class DailyTarotResponseSchema(CamelModel):
    model_config = ConfigDict(
        alias_generator=CamelModel.model_config.get("alias_generator"),
        populate_by_name=True,
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "uuid",
                "targetDate": "2026-04-10",
                "cardName": "Temperance",
                "cardOrientation": "upright",
                "question": "오늘 상대에게 먼저 연락해도 될까?",
                "aiInterpretation": (
                    "오늘은 서두르기보다 부드럽게 접근하는 편이 좋습니다. "
                    "짧고 가벼운 안부 메시지가 적합합니다."
                ),
            },
        },
    )

    id: str = Field(examples=["uuid"])
    target_date: date = Field(examples=["2026-04-10"])
    card_name: str = Field(examples=["Temperance"])
    card_orientation: str = Field(examples=["upright"])
    question: str = Field(examples=["오늘 상대에게 먼저 연락해도 될까?"])
    ai_interpretation: str = Field(
        examples=[
            "오늘은 서두르기보다 부드럽게 접근하는 편이 좋습니다. 짧고 가벼운 안부 메시지가 적합합니다."
        ],
    )
