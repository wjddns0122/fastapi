from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user, get_tarot_service
from app.core.response import success_response
from app.models.user import User
from app.schemas.common import SuccessResponseSchema
from app.schemas.tarot import (
    CreateDailyTarotRequestSchema,
    DailyTarotResponseSchema,
)
from app.services.tarot_service import TarotService
from app.utils.datetime import get_seoul_today

router = APIRouter()


@router.post(
    "/daily",
    summary="오늘의 타로 뽑기 및 해석",
    description=(
        "수락된 관계에 대해 오늘의 타로를 생성합니다.\n\n"
        "- 하루 1회 기준은 `사용자 + 관계 + 날짜` 입니다.\n"
        "- 이미 오늘 기록이 있으면 기존 결과를 반환합니다.\n"
        "- 카드 선택은 서버 룰 기반이며, 해석은 Gemini API를 사용합니다."
    ),
    response_model=SuccessResponseSchema[DailyTarotResponseSchema],
    responses={
        201: {
            "description": "오늘의 타로 생성 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": "uuid",
                            "targetDate": "2026-04-10",
                            "cardName": "Temperance",
                            "cardOrientation": "upright",
                            "question": "오늘 상대에게 먼저 연락해도 될까?",
                            "aiInterpretation": (
                                "오늘은 서두르기보다 부드럽게 접근하는 편이 좋습니다. "
                                "짧고 가벼운 안부 메시지가 적합합니다."
                            ),
                        },
                        "message": "오늘의 타로가 생성되었습니다.",
                    }
                }
            },
        },
        200: {
            "description": "오늘 이미 생성된 타로 반환",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": "uuid",
                            "targetDate": "2026-04-10",
                            "cardName": "Temperance",
                            "cardOrientation": "upright",
                            "question": "오늘 상대에게 먼저 연락해도 될까?",
                            "aiInterpretation": (
                                "오늘은 서두르기보다 부드럽게 접근하는 편이 좋습니다. "
                                "짧고 가벼운 안부 메시지가 적합합니다."
                            ),
                        },
                        "message": "OK",
                    }
                }
            },
        },
    },
)
def create_daily_tarot(
    request: CreateDailyTarotRequestSchema,
    current_user: User = Depends(get_current_user),
    tarot_service: TarotService = Depends(get_tarot_service),
):
    daily_tarot, created = tarot_service.create_daily_tarot(
        current_user=current_user,
        relationship_id=request.relationship_id,
        question=request.question,
        target_date=get_seoul_today(),
    )
    return success_response(
        data=DailyTarotResponseSchema.model_validate(daily_tarot),
        message="오늘의 타로가 생성되었습니다." if created else "OK",
        status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
    )


@router.get(
    "/daily/history",
    summary="내 타로 기록 조회",
    description="로그인한 사용자의 타로 기록을 최신순으로 조회합니다. `relationshipId` 필터를 사용할 수 있습니다.",
    response_model=SuccessResponseSchema[list[DailyTarotResponseSchema]],
    responses={
        200: {
            "description": "타로 기록 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": [
                            {
                                "id": "uuid",
                                "targetDate": "2026-04-10",
                                "cardName": "Temperance",
                                "cardOrientation": "upright",
                                "question": "오늘 상대에게 먼저 연락해도 될까?",
                                "aiInterpretation": (
                                    "오늘은 서두르기보다 부드럽게 접근하는 편이 좋습니다. "
                                    "짧고 가벼운 안부 메시지가 적합합니다."
                                ),
                            }
                        ],
                        "message": "OK",
                    }
                }
            },
        }
    },
)
def list_daily_tarot_history(
    relationship_id: str | None = Query(default=None, alias="relationshipId"),
    current_user: User = Depends(get_current_user),
    tarot_service: TarotService = Depends(get_tarot_service),
):
    daily_tarots = tarot_service.list_daily_tarot_history(
        current_user=current_user,
        relationship_id=relationship_id,
    )
    return success_response(
        data=[
            DailyTarotResponseSchema.model_validate(daily_tarot)
            for daily_tarot in daily_tarots
        ],
        message="OK",
    )
