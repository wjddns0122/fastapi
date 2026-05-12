from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, get_mission_service
from app.core.response import success_response
from app.models.user import User
from app.schemas.common import SuccessResponseSchema
from app.schemas.mission import (
    CompleteMissionRequestSchema,
    CompleteMissionResponseSchema,
    MissionResponseSchema,
)
from app.services.mission_service import MissionService
from app.utils.datetime import get_seoul_today

router = APIRouter()


@router.get(
    "/today",
    response_model=SuccessResponseSchema[list[MissionResponseSchema]],
    summary="오늘의 미션 조회",
)
def list_today_missions(
    relationship_id: str = Query(..., alias="relationshipId"),
    current_user: User = Depends(get_current_user),
    mission_service: MissionService = Depends(get_mission_service),
):
    missions = mission_service.list_today_missions(
        current_user=current_user,
        relationship_id=relationship_id,
        target_date=get_seoul_today(),
    )
    return success_response(
        data=[MissionResponseSchema.model_validate(mission) for mission in missions],
        message="OK",
    )


@router.post(
    "/{mission_id}/complete",
    response_model=SuccessResponseSchema[CompleteMissionResponseSchema],
    summary="미션 완료 처리",
)
def complete_mission(
    mission_id: str,
    request: CompleteMissionRequestSchema,
    current_user: User = Depends(get_current_user),
    mission_service: MissionService = Depends(get_mission_service),
):
    completion = mission_service.complete_mission(
        current_user=current_user,
        mission_id=mission_id,
        relationship_id=request.relationship_id,
        target_date=get_seoul_today(),
    )
    return success_response(
        data=CompleteMissionResponseSchema(
            mission_id=completion.mission_id,
            status="completed",
        ),
        message="미션이 완료되었습니다.",
    )
