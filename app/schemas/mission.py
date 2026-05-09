from typing import Literal

from pydantic import Field

from app.schemas.base import CamelModel

MissionStatus = Literal["pending", "completed"]


class MissionResponseSchema(CamelModel):
    """오늘의 미션 응답 스키마"""

    mission_id: str = Field(examples=["uuid"])
    title: str
    description: str
    reward_type: str = Field(examples=["points"])
    reward_value: int = Field(ge=0, examples=[10])
    status: MissionStatus = Field(examples=["pending"])


class CompleteMissionRequestSchema(CamelModel):
    """미션 완료 요청 스키마"""

    relationship_id: str = Field(examples=["uuid"])


class CompleteMissionResponseSchema(CamelModel):
    """미션 완료 응답 스키마"""

    mission_id: str
    status: MissionStatus
