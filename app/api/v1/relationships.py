from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user, get_relationship_service
from app.core.response import success_response
from app.models.user import User
from app.schemas.common import SuccessResponseSchema
from app.schemas.relationship import (
    CreateRelationshipRequestSchema,
    RelationshipCreateResponseSchema,
    RelationshipFilter,
    RelationshipListItemSchema,
    RelationshipStatus,
)
from app.services.relationship_service import RelationshipService

router = APIRouter()


@router.post(
    "",
    summary="관계 요청 생성",
    description="다른 사용자에게 친구, 연인 등의 관계를 요청합니다. relationshipType에는 'couple', 'situationship', 'friend' 중 하나를 입력해야 합니다.",
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
    """
    관계를 생성하기 위해 상대방에게 요청을 보냅니다.
    - **target_user_id**: 요청을 보낼 상대방의 UUID
    - **relationship_type**: 관계 유형 (couple, situationship, friend)
    """
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
    summary="관계 요청 수락",
    description="받은 관계 요청을 수락하여 관계를 활성화합니다.",
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
                            "status": "accepted",
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
    """
    나에게 온 관계 요청을 수락합니다.
    - **relationship_id**: 수락할 관계의 UUID
    """
    relationship = relationship_service.accept_relationship(
        relationship_id=relationship_id,
        current_user=current_user,
    )
    response_data = RelationshipCreateResponseSchema.model_validate(relationship)
    return success_response(
        data=response_data,
        message="관계 요청이 수락되었습니다.",
    )


@router.post(
    "/{relationship_id}/reject",
    summary="관계 요청 거절",
    description="받은 관계 요청을 거절합니다.",
    response_model=SuccessResponseSchema[RelationshipCreateResponseSchema],
    responses={
        200: {
            "description": "관계 요청 거절 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": "uuid",
                            "relationshipType": "couple",
                            "status": "rejected",
                        },
                        "message": "관계 요청이 거절되었습니다.",
                    }
                }
            },
        }
    },
)
def reject_relationship(
    relationship_id: str,
    current_user: User = Depends(get_current_user),
    relationship_service: RelationshipService = Depends(get_relationship_service),
):
    """
    나에게 온 관계 요청을 거절합니다.
    - **relationship_id**: 거절할 관계의 UUID
    """
    relationship = relationship_service.reject_relationship(
        relationship_id=relationship_id,
        current_user=current_user,
    )
    response_data = RelationshipCreateResponseSchema.model_validate(relationship)
    return success_response(
        data=response_data,
        message="관계 요청이 거절되었습니다.",
    )


@router.delete(
    "/{relationship_id}",
    summary="관계 삭제 또는 요청 취소",
    description="기존 관계를 해제하거나, 내가 보낸 대기 중인 요청을 취소합니다.",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponseSchema[None],
    responses={
        200: {
            "description": "관계 삭제 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": None,
                        "message": "관계가 삭제되었습니다.",
                    }
                }
            },
        }
    },
)
def delete_relationship(
    relationship_id: str,
    current_user: User = Depends(get_current_user),
    relationship_service: RelationshipService = Depends(get_relationship_service),
):
    """
    관계를 삭제하거나 내가 보낸 요청을 취소합니다.
    - **relationship_id**: 삭제할 관계의 UUID
    """
    relationship_service.delete_relationship(
        relationship_id=relationship_id,
        current_user=current_user,
    )
    return success_response(data=None, message="관계가 삭제되었습니다.")


@router.get(
    "/me",
    summary="내 관계 목록 조회",
    description="현재 내가 맺고 있는 관계 목록을 조회합니다. status(pending/accepted/rejected) 및 filter(sent/received)로 필터링할 수 있습니다.",
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
                                "status": "accepted",
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
    status: Optional[RelationshipStatus] = Query(
        default=None,
        description="관계 상태 필터 (pending: 대기, accepted: 수락, rejected: 거절)",
    ),
    filter: Optional[RelationshipFilter] = Query(
        default=None,
        description="방향 필터 (sent: 내가 보낸 요청, received: 내가 받은 요청)",
    ),
    current_user: User = Depends(get_current_user),
    relationship_service: RelationshipService = Depends(get_relationship_service),
):
    """
    로그인한 사용자의 관계 목록을 가져옵니다.
    - **status**: 상태 필터 (pending / accepted / rejected)
    - **filter**: 방향 필터 (sent / received)
    """
    relationships = relationship_service.list_my_relationships(
        current_user=current_user,
        status=status,
        filter=filter,
    )
    response_data = [
        RelationshipListItemSchema.model_validate(relationship)
        for relationship in relationships
    ]
    return success_response(
        data=response_data,
        message="OK",
    )
