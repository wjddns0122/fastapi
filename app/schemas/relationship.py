from typing import Literal

from pydantic import ConfigDict, Field

from app.schemas.base import CamelModel

RelationshipType = Literal["couple", "situationship", "friend"]
RelationshipStatus = Literal["pending", "active"]


class CreateRelationshipRequestSchema(CamelModel):
    """관계(친구/연인 등) 생성 요청 스키마"""
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

    target_user_id: str = Field(description="대상 사용자 UUID", examples=["uuid"])
    relationship_type: RelationshipType = Field(
        description="관계 유형 (couple: 연인, situationship: 썸, friend: 친구)",
        examples=["couple"],
    )


class RelationshipCreateResponseSchema(CamelModel):
    """관계 생성 응답 스키마"""
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

    id: str = Field(description="관계 UUID", examples=["uuid"])
    relationship_type: RelationshipType = Field(
        description="관계 유형 (couple: 연인, situationship: 썸, friend: 친구)",
        examples=["couple"],
    )
    status: RelationshipStatus = Field(description="관계 상태 (pending/active)", examples=["pending"])


class RelationshipPartnerSchema(CamelModel):
    id: str = Field(examples=["uuid"])
    nickname: str = Field(examples=["partner"])


class RelationshipListItemSchema(CamelModel):
    """관계 목록 아이템 스키마"""
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

    id: str = Field(description="관계 UUID", examples=["uuid"])
    relationship_type: RelationshipType = Field(
        description="관계 유형 (couple: 연인, situationship: 썸, friend: 친구)",
        examples=["couple"],
    )
    status: RelationshipStatus = Field(description="관계 상태", examples=["active"])
    partner: RelationshipPartnerSchema = Field(description="상대방 정보")
