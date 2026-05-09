from fastapi import APIRouter, Depends, status

from app.api.deps import get_compatibility_service, get_current_user
from app.core.response import success_response
from app.models.user import User
from app.schemas.common import SuccessResponseSchema
from app.schemas.compatibility import DailyCompatibilityResponseSchema
from app.services.compatibility_service import CompatibilityService
from app.utils.datetime import get_seoul_today

router = APIRouter()


@router.get(
    "/today/{relationship_id}",
    response_model=SuccessResponseSchema[DailyCompatibilityResponseSchema],
    summary="오늘의 궁합 조회",
)
def get_today_compatibility(
    relationship_id: str,
    current_user: User = Depends(get_current_user),
    compatibility_service: CompatibilityService = Depends(get_compatibility_service),
):
    daily_compatibility = compatibility_service.get_today_compatibility(
        current_user=current_user,
        relationship_id=relationship_id,
        target_date=get_seoul_today(),
    )
    return success_response(
        data=DailyCompatibilityResponseSchema.model_validate(daily_compatibility),
        message="OK",
    )


@router.post(
    "/today/{relationship_id}/refresh",
    response_model=SuccessResponseSchema[DailyCompatibilityResponseSchema],
    summary="오늘의 궁합 재계산",
)
def refresh_today_compatibility(
    relationship_id: str,
    current_user: User = Depends(get_current_user),
    compatibility_service: CompatibilityService = Depends(get_compatibility_service),
):
    daily_compatibility = compatibility_service.refresh_today_compatibility(
        current_user=current_user,
        relationship_id=relationship_id,
        target_date=get_seoul_today(),
    )
    return success_response(
        data=DailyCompatibilityResponseSchema.model_validate(daily_compatibility),
        message="오늘의 궁합이 재계산되었습니다.",
        status_code=status.HTTP_200_OK,
    )
