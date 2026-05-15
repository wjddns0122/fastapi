from datetime import date

from pydantic import Field

from app.schemas.base import CamelModel
from app.schemas.compatibility import DailyCompatibilityResponseSchema
from app.schemas.mission import MissionResponseSchema


class TarotPreviewSchema(CamelModel):
    card_name: str
    card_orientation: str
    message: str


class LetterCtaSchema(CamelModel):
    action: str = Field(examples=["write_letter"])
    label: str
    suggested_prompt: str


class RecentScoreSchema(CamelModel):
    target_date: date
    final_score: int = Field(ge=0, le=100)


class HomeTodayResponseSchema(CamelModel):
    relationship_id: str
    compatibility: DailyCompatibilityResponseSchema
    keywords: list[str]
    tarot_preview: TarotPreviewSchema
    missions: list[MissionResponseSchema]
    letter_cta: LetterCtaSchema
    recent_scores: list[RecentScoreSchema]
