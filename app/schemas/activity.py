from datetime import date
from typing import Any, Literal

from pydantic import ConfigDict, Field

from app.schemas.base import CamelModel

RelationshipActivityEventType = Literal[
    "letter_sent",
    "letter_opened",
    "daily_quest_completed",
    "weekly_quest_completed",
    "shop_visited",
    "avatar_changed",
    "couple_item_equipped",
    "checkin_completed",
]


class RecordRelationshipActivityRequestSchema(CamelModel):
    model_config = ConfigDict(
        alias_generator=CamelModel.model_config.get("alias_generator"),
        populate_by_name=True,
        from_attributes=True,
        json_schema_extra={
            "example": {
                "eventType": "avatar_changed",
                "occurredOn": "2026-04-10",
                "metadata": {
                    "itemKey": "spring-jacket",
                },
            },
        },
    )

    event_type: RelationshipActivityEventType = Field(examples=["avatar_changed"])
    occurred_on: date | None = Field(default=None, examples=["2026-04-10"])
    metadata: dict[str, Any] = Field(default_factory=dict, examples=[{"itemKey": "spring-jacket"}])


class ShopVisitRequestSchema(CamelModel):
    occurred_on: date | None = Field(default=None, examples=["2026-04-10"])
    metadata: dict[str, Any] = Field(default_factory=dict, examples=[{"shopSection": "spring"}])


class AvatarChangeRequestSchema(CamelModel):
    occurred_on: date | None = Field(default=None, examples=["2026-04-10"])
    metadata: dict[str, Any] = Field(default_factory=dict, examples=[{"itemKey": "spring-jacket"}])


class CoupleItemEquipRequestSchema(CamelModel):
    occurred_on: date | None = Field(default=None, examples=["2026-04-10"])
    metadata: dict[str, Any] = Field(default_factory=dict, examples=[{"itemKey": "matching-hat"}])


class QuestCompleteRequestSchema(CamelModel):
    occurred_on: date | None = Field(default=None, examples=["2026-04-10"])
    metadata: dict[str, Any] = Field(default_factory=dict, examples=[{"questKey": "daily-greeting"}])


class CheckinRequestSchema(CamelModel):
    occurred_on: date | None = Field(default=None, examples=["2026-04-10"])
    metadata: dict[str, Any] = Field(default_factory=dict, examples=[{"mood": "happy"}])


class LetterActivityRequestSchema(CamelModel):
    occurred_on: date | None = Field(default=None, examples=["2026-04-10"])
    metadata: dict[str, Any] = Field(default_factory=dict, examples=[{"letterId": "uuid"}])


class RelationshipActivityResponseSchema(CamelModel):
    model_config = ConfigDict(
        alias_generator=CamelModel.model_config.get("alias_generator"),
        populate_by_name=True,
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "uuid",
                "relationshipId": "uuid",
                "actorUserId": "uuid",
                "eventType": "avatar_changed",
                "occurredOn": "2026-04-10",
                "metadata": {
                    "itemKey": "spring-jacket",
                },
            },
        },
    )

    id: str = Field(examples=["uuid"])
    relationship_id: str = Field(examples=["uuid"])
    actor_user_id: str = Field(examples=["uuid"])
    event_type: RelationshipActivityEventType = Field(examples=["avatar_changed"])
    occurred_on: date = Field(examples=["2026-04-10"])
    event_metadata: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias="event_metadata",
        serialization_alias="metadata",
    )
