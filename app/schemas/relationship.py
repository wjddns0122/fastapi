from typing import Literal

from pydantic import ConfigDict, Field

from app.schemas.base import CamelModel

RelationshipType = Literal["couple", "situationship", "friend"]
RelationshipStatus = Literal["pending", "active"]


class CreateRelationshipRequestSchema(CamelModel):
    model_config = ConfigDict(
        alias_generator=CamelModel.model_config.get("alias_generator"),
        populate_by_name=True,
        from_attributes=True,
        json_schema_extra={
            "example": {
                "targetUserId": "uuid",
                "relationshipType": "couple",
            },
        },
    )

    target_user_id: str = Field(examples=["uuid"])
    relationship_type: RelationshipType = Field(examples=["couple"])


class RelationshipCreateResponseSchema(CamelModel):
    model_config = ConfigDict(
        alias_generator=CamelModel.model_config.get("alias_generator"),
        populate_by_name=True,
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "uuid",
                "relationshipType": "couple",
                "status": "pending",
            },
        },
    )

    id: str = Field(examples=["uuid"])
    relationship_type: RelationshipType = Field(examples=["couple"])
    status: RelationshipStatus = Field(examples=["pending"])


class RelationshipPartnerSchema(CamelModel):
    id: str = Field(examples=["uuid"])
    nickname: str = Field(examples=["partner"])


class RelationshipListItemSchema(CamelModel):
    model_config = ConfigDict(
        alias_generator=CamelModel.model_config.get("alias_generator"),
        populate_by_name=True,
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "uuid",
                "relationshipType": "couple",
                "status": "active",
                "partner": {
                    "id": "uuid",
                    "nickname": "partner",
                },
            },
        },
    )

    id: str = Field(examples=["uuid"])
    relationship_type: RelationshipType = Field(examples=["couple"])
    status: RelationshipStatus = Field(examples=["active"])
    partner: RelationshipPartnerSchema
