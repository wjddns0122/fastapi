from fastapi import APIRouter, Depends, Header

from app.api.deps import get_compatibility_service, get_current_user
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.response import success_response
from app.models.user import User
from app.schemas.common import SuccessResponseSchema
from app.schemas.compatibility import DailyCompatibilityResponseSchema
from app.services.compatibility_service import CompatibilityService
from app.utils.datetime import get_seoul_today

router = APIRouter()


def _serialize(record) -> DailyCompatibilityResponseSchema:
    return DailyCompatibilityResponseSchema.model_validate(record)


@router.get(
    "/today/{relationship_id}",
    summary="오늘의 궁합 조회",
    description="오늘 궁합 데이터를 조회합니다. 오늘 데이터가 없으면 계산 후 저장해서 반환합니다.",
    response_model=SuccessResponseSchema[DailyCompatibilityResponseSchema],
    responses={
        200: {
            "description": "오늘의 궁합 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "relationshipId": "uuid",
                            "targetDate": "2026-04-10",
                            "baseScore": 62,
                            "tarotScore": 10,
                            "behaviorScore": 8,
                            "finalScore": 80,
                            "summary": "오늘은 대화 흐름이 좋고, 먼저 안부를 건네면 분위기가 더 좋아질 수 있습니다.",
                            "prescription": "가벼운 칭찬 한 마디를 먼저 건네보세요.",
                        },
                        "message": "OK",
                    }
                }
            },
        }
    },
)
def get_today_compatibility(
    relationship_id: str,
    current_user: User = Depends(get_current_user),
    compatibility_service: CompatibilityService = Depends(get_compatibility_service),
):
    record = compatibility_service.get_today_compatibility(
        relationship_id=relationship_id,
        current_user=current_user,
        target_date=get_seoul_today(),
    )
    return success_response(data=_serialize(record), message="OK")


@router.post(
    "/today/{relationship_id}/refresh",
    summary="오늘의 궁합 재계산",
    description="내부/관리자용 강제 재계산 엔드포인트입니다. `X-Internal-Token` 헤더가 필요합니다.",
    response_model=SuccessResponseSchema[DailyCompatibilityResponseSchema],
    include_in_schema=False,
)
def refresh_today_compatibility(
    relationship_id: str,
    x_internal_token: str | None = Header(default=None, alias="X-Internal-Token"),
    current_user: User = Depends(get_current_user),
    compatibility_service: CompatibilityService = Depends(get_compatibility_service),
):
    if settings.compatibility_refresh_token is None or x_internal_token != settings.compatibility_refresh_token:
        raise AppException(
            code="FORBIDDEN",
            message="궁합 재계산 권한이 없습니다.",
            status_code=403,
        )

    record = compatibility_service.refresh_today_compatibility(
        relationship_id=relationship_id,
        current_user=current_user,
        target_date=get_seoul_today(),
    )
    return success_response(
        data=_serialize(record),
        message="오늘의 궁합이 재계산되었습니다.",
    )
