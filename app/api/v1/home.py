from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, get_home_service
from app.core.response import success_response
from app.models.user import User
from app.schemas.common import SuccessResponseSchema
from app.schemas.home import HomeTodayResponseSchema
from app.services.home_service import HomeService
from app.utils.datetime import get_seoul_today

router = APIRouter()


@router.get(
    "/today",
    response_model=SuccessResponseSchema[HomeTodayResponseSchema],
    summary="오늘 홈 화면 통합 조회",
)
def get_today_home(
    relationship_id: str | None = Query(default=None, alias="relationshipId"),
    current_user: User = Depends(get_current_user),
    home_service: HomeService = Depends(get_home_service),
):
    data = home_service.get_today_home(
        current_user=current_user,
        target_date=get_seoul_today(),
        relationship_id=relationship_id,
    )
    return success_response(
        data=HomeTodayResponseSchema.model_validate(data),
        message="OK",
    )
