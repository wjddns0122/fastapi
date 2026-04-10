from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user, get_relationship_service
from app.core.response import success_response
from app.models.user import User
from app.schemas.common import SuccessResponseSchema
from app.schemas.relationship import (
    CreateRelationshipRequestSchema,
    RelationshipCreateResponseSchema,
    RelationshipListItemSchema,
)
from app.services.relationship_service import RelationshipService

router = APIRouter()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseSchema[RelationshipCreateResponseSchema],
    responses={
        201: {
            "description": "관계 요청 생성 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": "uuid",
                            "relationshipType": "couple",
                            "status": "pending",
                        },
                        "message": "관계 요청이 생성되었습니다.",
                    }
                }
            },
        }
    },
)
def create_relationship(
    request: CreateRelationshipRequestSchema,
    current_user: User = Depends(get_current_user),
    relationship_service: RelationshipService = Depends(get_relationship_service),
):
    relationship = relationship_service.create_relationship(
        current_user=current_user,
        target_user_id=request.target_user_id,
        relationship_type=request.relationship_type,
    )
    response_data = RelationshipCreateResponseSchema.model_validate(relationship)
    return success_response(
        data=response_data,
        message="관계 요청이 생성되었습니다.",
        status_code=status.HTTP_201_CREATED,
    )


@router.post(
    "/{relationship_id}/accept",
    response_model=SuccessResponseSchema[RelationshipCreateResponseSchema],
    responses={
        200: {
            "description": "관계 요청 수락 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": "uuid",
                            "relationshipType": "couple",
                            "status": "active",
                        },
                        "message": "관계 요청이 수락되었습니다.",
                    }
                }
            },
        }
    },
)
def accept_relationship(
    relationship_id: str,
    current_user: User = Depends(get_current_user),
    relationship_service: RelationshipService = Depends(get_relationship_service),
):
    relationship = relationship_service.accept_relationship(
        relationship_id=relationship_id,
        current_user=current_user,
    )
    response_data = RelationshipCreateResponseSchema.model_validate(relationship)
    return success_response(
        data=response_data,
        message="관계 요청이 수락되었습니다.",
    )


@router.get(
    "/me",
    response_model=SuccessResponseSchema[list[RelationshipListItemSchema]],
    responses={
        200: {
            "description": "내 관계 목록 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": [
                            {
                                "id": "uuid",
                                "relationshipType": "couple",
                                "status": "active",
                                "partner": {
                                    "id": "uuid",
                                    "nickname": "partner",
                                },
                            }
                        ],
                        "message": "OK",
                    }
                }
            },
        }
    },
)
def list_my_relationships(
    current_user: User = Depends(get_current_user),
    relationship_service: RelationshipService = Depends(get_relationship_service),
):
    relationships = relationship_service.list_my_relationships(current_user=current_user)
    response_data = [
        RelationshipListItemSchema.model_validate(relationship)
        for relationship in relationships
    ]
    return success_response(
        data=response_data,
        message="OK",
    )
