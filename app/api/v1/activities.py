from fastapi import APIRouter, Depends, status

from app.api.deps import get_activity_service, get_current_user
from app.core.response import success_response
from app.models.user import User
from app.schemas.activity import (
    AvatarChangeRequestSchema,
    CheckinRequestSchema,
    CoupleItemEquipRequestSchema,
    LetterActivityRequestSchema,
    QuestCompleteRequestSchema,
    RecordRelationshipActivityRequestSchema,
    RelationshipActivityResponseSchema,
    ShopVisitRequestSchema,
)
from app.schemas.common import SuccessResponseSchema
from app.services.activity_service import ActivityService

router = APIRouter()


def _record_activity_response(
    relationship_id: str,
    current_user: User,
    activity_service: ActivityService,
    event_type: str,
    occurred_on,
    metadata: dict[str, object],
):
    activity = activity_service.record_relationship_activity(
        relationship_id=relationship_id,
        current_user=current_user,
        event_type=event_type,
        occurred_on=occurred_on,
        metadata=metadata,
    )
    return success_response(
        data=RelationshipActivityResponseSchema.model_validate(activity),
        message="활동이 기록되었습니다.",
        status_code=status.HTTP_201_CREATED,
    )


@router.post(
    "/relationships/{relationship_id}/activities",
    summary="관계 활동 기록",
    description=(
        "궁합 계산에 반영되는 관계 활동 이벤트를 기록합니다.\n\n"
        "- 편지, 퀘스트, 상점 방문, 아바타 변경, 커플 아이템 장착, 감정 체크 등을 기록할 수 있습니다.\n"
        "- 수락된 관계의 당사자만 기록할 수 있습니다.\n"
        "- `occurredOn` 을 생략하면 서울 기준 오늘 날짜로 저장됩니다."
    ),
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseSchema[RelationshipActivityResponseSchema],
    responses={
        201: {
            "description": "활동 기록 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": "uuid",
                            "relationshipId": "uuid",
                            "actorUserId": "uuid",
                            "eventType": "avatar_changed",
                            "occurredOn": "2026-04-10",
                            "metadata": {
                                "itemKey": "spring-jacket",
                            },
                        },
                        "message": "활동이 기록되었습니다.",
                    }
                }
            },
        }
    },
)
def record_relationship_activity(
    relationship_id: str,
    request: RecordRelationshipActivityRequestSchema,
    current_user: User = Depends(get_current_user),
    activity_service: ActivityService = Depends(get_activity_service),
):
    return _record_activity_response(
        relationship_id=relationship_id,
        current_user=current_user,
        activity_service=activity_service,
        event_type=request.event_type,
        occurred_on=request.occurred_on,
        metadata=request.metadata,
    )


@router.post(
    "/relationships/{relationship_id}/shop/visit",
    summary="상점 방문 기록",
    description="상점 진입 이벤트를 기록합니다. 오늘 궁합의 활동 점수에 반영됩니다.",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseSchema[RelationshipActivityResponseSchema],
)
def record_shop_visit(
    relationship_id: str,
    request: ShopVisitRequestSchema,
    current_user: User = Depends(get_current_user),
    activity_service: ActivityService = Depends(get_activity_service),
):
    return _record_activity_response(
        relationship_id=relationship_id,
        current_user=current_user,
        activity_service=activity_service,
        event_type="shop_visited",
        occurred_on=request.occurred_on,
        metadata=request.metadata,
    )


@router.post(
    "/relationships/{relationship_id}/avatar/change",
    summary="아바타 변경 기록",
    description="아바타 의상 또는 스타일 변경 이벤트를 기록합니다.",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseSchema[RelationshipActivityResponseSchema],
)
def record_avatar_change(
    relationship_id: str,
    request: AvatarChangeRequestSchema,
    current_user: User = Depends(get_current_user),
    activity_service: ActivityService = Depends(get_activity_service),
):
    return _record_activity_response(
        relationship_id=relationship_id,
        current_user=current_user,
        activity_service=activity_service,
        event_type="avatar_changed",
        occurred_on=request.occurred_on,
        metadata=request.metadata,
    )


@router.post(
    "/relationships/{relationship_id}/items/couple/equip",
    summary="커플 아이템 장착 기록",
    description="커플 아이템 장착 이벤트를 기록합니다. 양측 모두 기록되면 추가 점수가 반영됩니다.",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseSchema[RelationshipActivityResponseSchema],
)
def record_couple_item_equip(
    relationship_id: str,
    request: CoupleItemEquipRequestSchema,
    current_user: User = Depends(get_current_user),
    activity_service: ActivityService = Depends(get_activity_service),
):
    return _record_activity_response(
        relationship_id=relationship_id,
        current_user=current_user,
        activity_service=activity_service,
        event_type="couple_item_equipped",
        occurred_on=request.occurred_on,
        metadata=request.metadata,
    )


@router.post(
    "/relationships/{relationship_id}/quests/daily/complete",
    summary="일일 퀘스트 완료 기록",
    description="일일 퀘스트 완료 이벤트를 기록합니다.",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseSchema[RelationshipActivityResponseSchema],
)
def record_daily_quest_complete(
    relationship_id: str,
    request: QuestCompleteRequestSchema,
    current_user: User = Depends(get_current_user),
    activity_service: ActivityService = Depends(get_activity_service),
):
    return _record_activity_response(
        relationship_id=relationship_id,
        current_user=current_user,
        activity_service=activity_service,
        event_type="daily_quest_completed",
        occurred_on=request.occurred_on,
        metadata=request.metadata,
    )


@router.post(
    "/relationships/{relationship_id}/quests/weekly/complete",
    summary="주간 퀘스트 완료 기록",
    description="주간 퀘스트 완료 이벤트를 기록합니다.",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseSchema[RelationshipActivityResponseSchema],
)
def record_weekly_quest_complete(
    relationship_id: str,
    request: QuestCompleteRequestSchema,
    current_user: User = Depends(get_current_user),
    activity_service: ActivityService = Depends(get_activity_service),
):
    return _record_activity_response(
        relationship_id=relationship_id,
        current_user=current_user,
        activity_service=activity_service,
        event_type="weekly_quest_completed",
        occurred_on=request.occurred_on,
        metadata=request.metadata,
    )


@router.post(
    "/relationships/{relationship_id}/checkins",
    summary="감정 체크 기록",
    description="오늘의 감정 체크 완료 이벤트를 기록합니다.",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseSchema[RelationshipActivityResponseSchema],
)
def record_checkin(
    relationship_id: str,
    request: CheckinRequestSchema,
    current_user: User = Depends(get_current_user),
    activity_service: ActivityService = Depends(get_activity_service),
):
    return _record_activity_response(
        relationship_id=relationship_id,
        current_user=current_user,
        activity_service=activity_service,
        event_type="checkin_completed",
        occurred_on=request.occurred_on,
        metadata=request.metadata,
    )


@router.post(
    "/relationships/{relationship_id}/letters/send",
    summary="편지 작성 기록",
    description="편지 작성 이벤트를 기록합니다.",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseSchema[RelationshipActivityResponseSchema],
)
def record_letter_sent(
    relationship_id: str,
    request: LetterActivityRequestSchema,
    current_user: User = Depends(get_current_user),
    activity_service: ActivityService = Depends(get_activity_service),
):
    return _record_activity_response(
        relationship_id=relationship_id,
        current_user=current_user,
        activity_service=activity_service,
        event_type="letter_sent",
        occurred_on=request.occurred_on,
        metadata=request.metadata,
    )


@router.post(
    "/relationships/{relationship_id}/letters/open",
    summary="편지 열람 기록",
    description="상대 편지 열람 이벤트를 기록합니다.",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseSchema[RelationshipActivityResponseSchema],
)
def record_letter_opened(
    relationship_id: str,
    request: LetterActivityRequestSchema,
    current_user: User = Depends(get_current_user),
    activity_service: ActivityService = Depends(get_activity_service),
):
    return _record_activity_response(
        relationship_id=relationship_id,
        current_user=current_user,
        activity_service=activity_service,
        event_type="letter_opened",
        occurred_on=request.occurred_on,
        metadata=request.metadata,
    )
