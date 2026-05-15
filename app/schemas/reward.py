from pydantic import Field

from app.schemas.base import CamelModel


class RewardProfileSchema(CamelModel):
    relationship_id: str
    points: int = Field(ge=0)
    experience: int = Field(ge=0)
    level: int = Field(ge=1)
    streak_days: int = Field(ge=0)
    badges: list[str]
