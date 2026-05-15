from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_reward_service
from app.core.response import success_response
from app.models.user import User
from app.schemas.common import SuccessResponseSchema
from app.schemas.reward import RewardProfileSchema
from app.services.reward_service import RewardService
from app.utils.datetime import get_seoul_today

router = APIRouter()


@router.get(
    "/relationships/{relationship_id}",
    response_model=SuccessResponseSchema[RewardProfileSchema],
    summary="관계 보상 프로필 조회",
)
def get_relationship_reward_profile(
    relationship_id: str,
    current_user: User = Depends(get_current_user),
    reward_service: RewardService = Depends(get_reward_service),
):
    profile = reward_service.get_reward_profile(
        current_user=current_user,
        relationship_id=relationship_id,
        today=get_seoul_today(),
    )
    return success_response(
        data=RewardProfileSchema.model_validate(profile),
        message="OK",
    )
