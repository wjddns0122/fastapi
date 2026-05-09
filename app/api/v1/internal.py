from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Header

from app.api.deps import (
    get_compatibility_service,
    get_letter_service,
    get_report_service,
)
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.response import success_response
from app.services.compatibility_service import CompatibilityService
from app.services.letter_service import LetterService
from app.services.report_service import ReportService
from app.utils.datetime import get_seoul_today

router = APIRouter()


def verify_internal_secret(
    x_internal_secret: str | None = Header(default=None),
) -> None:
    if not settings.internal_secret or x_internal_secret != settings.internal_secret:
        raise AppException(
            code="UNAUTHORIZED",
            message="내부 API 인증이 필요합니다.",
            status_code=401,
        )


@router.post("/compatibility/generate-daily", summary="일간 궁합 배치 생성")
def generate_daily_compatibility(
    _: None = Depends(verify_internal_secret),
    compatibility_service: CompatibilityService = Depends(get_compatibility_service),
):
    generated_count = compatibility_service.generate_daily_for_all(
        target_date=get_seoul_today(),
    )
    return success_response(
        data={"generatedCount": generated_count},
        message="일간 궁합 생성이 완료되었습니다.",
    )


@router.post("/letters/send-scheduled", summary="예약 편지 발송 배치")
def send_scheduled_letters(
    _: None = Depends(verify_internal_secret),
    letter_service: LetterService = Depends(get_letter_service),
):
    sent_count = letter_service.send_scheduled_letters(now=datetime.now(UTC))
    return success_response(
        data={"sentCount": sent_count},
        message="예약 편지 발송이 완료되었습니다.",
    )


@router.post("/reports/generate-weekly", summary="주간 리포트 배치 생성")
def generate_weekly_reports(
    _: None = Depends(verify_internal_secret),
    report_service: ReportService = Depends(get_report_service),
):
    generated_count = report_service.generate_weekly_for_all(today=get_seoul_today())
    return success_response(
        data={"generatedCount": generated_count},
        message="주간 리포트 생성이 완료되었습니다.",
    )
