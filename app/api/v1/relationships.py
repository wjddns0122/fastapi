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

_401 = {
    "description": "인증 토큰 누락 또는 만료",
    "content": {
        "application/json": {
            "example": {"success": False, "error": {"code": "UNAUTHORIZED", "message": "인증이 필요합니다."}}
        }
    },
}
_403 = {
    "description": "권한 없음 (요청 대상자가 아닌 사용자가 상태 변경 시도)",
    "content": {
        "application/json": {
            "example": {"success": False, "error": {"code": "FORBIDDEN", "message": "관계 요청을 처리할 권한이 없습니다."}}
        }
    },
}
_404 = {
    "description": "관계를 찾을 수 없음",
    "content": {
        "application/json": {
            "example": {"success": False, "error": {"code": "NOT_FOUND", "message": "관계 요청을 찾을 수 없습니다."}}
        }
    },
}
_409 = {
    "description": "이미 처리된 요청 또는 중복 요청",
    "content": {
        "application/json": {
            "example": {"success": False, "error": {"code": "CONFLICT", "message": "이미 처리된 관계 요청입니다."}}
        }
    },
}
_422 = {
    "description": "요청 데이터 유효성 오류",
    "content": {
        "application/json": {
            "example": {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "요청 데이터를 확인해주세요.",
                    "details": [{"loc": ["body", "relationshipType"], "msg": "unexpected value; permitted: 'couple', 'situationship', 'friend'", "type": "type_error.enum"}],
                },
            }
        }
    },
}


@router.post(
    "",
    summary="관계 요청 생성",
    description=(
        "다른 사용자에게 관계 요청을 보냅니다.\n\n"
        "**관계 유형 (`relationshipType`)**\n"
        "- `couple` — 연인\n"
        "- `situationship` — 썸\n"
        "- `friend` — 친구\n\n"
        "**제약 조건**\n"
        "- 자기 자신에게는 요청할 수 없습니다. (400)\n"
        "- 대상 사용자가 존재하지 않으면 404를 반환합니다.\n"
        "- 두 사용자 간에 이미 관계(pending 포함)가 존재하면 409를 반환합니다.\n"
        "- `Authorization: Bearer <accessToken>` 헤더가 필요합니다."
    ),
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
                            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "relationshipType": "couple",
                            "status": "pending",
                        },
                        "message": "관계 요청이 생성되었습니다.",
                    }
                }
            },
        },
        400: {
            "description": "자기 자신에게 요청하는 경우",
            "content": {
                "application/json": {
                    "example": {"success": False, "error": {"code": "BAD_REQUEST", "message": "자기 자신과의 관계는 생성할 수 없습니다."}}
                }
            },
        },
        401: _401,
        404: {
            "description": "대상 사용자를 찾을 수 없음",
            "content": {
                "application/json": {
                    "example": {"success": False, "error": {"code": "NOT_FOUND", "message": "대상 사용자를 찾을 수 없습니다."}}
                }
            },
        },
        409: {
            "description": "두 사용자 간 관계가 이미 존재함",
            "content": {
                "application/json": {
                    "example": {"success": False, "error": {"code": "CONFLICT", "message": "이미 관계 요청이 존재합니다."}}
                }
            },
        },
        422: _422,
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
    summary="관계 요청 수락",
    description=(
        "나에게 온 관계 요청을 수락합니다.\n\n"
        "**제약 조건**\n"
        "- 요청의 대상자(`targetUserId`)만 수락할 수 있습니다. 요청자가 시도하면 403을 반환합니다.\n"
        "- `pending` 상태인 요청만 수락할 수 있습니다. 이미 처리된 요청이면 409를 반환합니다.\n"
        "- `Authorization: Bearer <accessToken>` 헤더가 필요합니다."
    ),
    response_model=SuccessResponseSchema[RelationshipCreateResponseSchema],
    responses={
        200: {
            "description": "관계 요청 수락 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "relationshipType": "couple",
                            "status": "accepted",
                        },
                        "message": "관계 요청이 수락되었습니다.",
                    }
                }
            },
        },
        401: _401,
        403: _403,
        404: _404,
        409: _409,
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


@router.post(
    "/{relationship_id}/reject",
    summary="관계 요청 거절",
    description=(
        "나에게 온 관계 요청을 거절합니다.\n\n"
        "**제약 조건**\n"
        "- 요청의 대상자(`targetUserId`)만 거절할 수 있습니다. 요청자가 시도하면 403을 반환합니다.\n"
        "- `pending` 상태인 요청만 거절할 수 있습니다. 이미 처리된 요청이면 409를 반환합니다.\n"
        "- `Authorization: Bearer <accessToken>` 헤더가 필요합니다."
    ),
    response_model=SuccessResponseSchema[RelationshipCreateResponseSchema],
    responses={
        200: {
            "description": "관계 요청 거절 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "relationshipType": "friend",
                            "status": "rejected",
                        },
                        "message": "관계 요청이 거절되었습니다.",
                    }
                }
            },
        },
        401: _401,
        403: _403,
        404: _404,
        409: _409,
    },
)
def reject_relationship(
    relationship_id: str,
    current_user: User = Depends(get_current_user),
    relationship_service: RelationshipService = Depends(get_relationship_service),
):
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
    description=(
        "기존 관계를 해제하거나, 내가 보낸 대기 중인 요청을 취소합니다.\n\n"
        "**제약 조건**\n"
        "- 해당 관계의 요청자 또는 대상자만 삭제할 수 있습니다. 관계 당사자가 아니면 403을 반환합니다.\n"
        "- `Authorization: Bearer <accessToken>` 헤더가 필요합니다."
    ),
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
        },
        401: _401,
        403: {
            "description": "관계 당사자가 아닌 사용자가 삭제 시도",
            "content": {
                "application/json": {
                    "example": {"success": False, "error": {"code": "FORBIDDEN", "message": "관계를 삭제할 권한이 없습니다."}}
                }
            },
        },
        404: _404,
    },
)
def delete_relationship(
    relationship_id: str,
    current_user: User = Depends(get_current_user),
    relationship_service: RelationshipService = Depends(get_relationship_service),
):
    relationship_service.delete_relationship(
        relationship_id=relationship_id,
        current_user=current_user,
    )
    return success_response(data=None, message="관계가 삭제되었습니다.")


@router.get(
    "/me",
    summary="내 관계 목록 조회",
    description=(
        "현재 내가 맺고 있는 관계 목록을 조회합니다.\n\n"
        "**쿼리 파라미터로 필터링 가능**\n"
        "- `status` — 관계 상태 필터\n"
        "  - `pending`: 아직 수락/거절되지 않은 대기 중인 요청\n"
        "  - `accepted`: 수락된 관계\n"
        "  - `rejected`: 거절된 관계\n"
        "- `filter` — 방향 필터\n"
        "  - `sent`: 내가 보낸 요청만\n"
        "  - `received`: 내가 받은 요청만\n\n"
        "두 파라미터를 동시에 사용할 수 있습니다. 파라미터를 생략하면 전체 목록을 반환합니다.\n\n"
        "- `Authorization: Bearer <accessToken>` 헤더가 필요합니다."
    ),
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
                                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                "relationshipType": "couple",
                                "status": "accepted",
                                "partner": {
                                    "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                                    "nickname": "partner_nickname",
                                },
                            }
                        ],
                        "message": "OK",
                    }
                }
            },
        },
        401: _401,
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
