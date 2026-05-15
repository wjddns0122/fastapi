from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_report_service
from app.core.response import success_response
from app.models.user import User
from app.schemas.common import SuccessResponseSchema
from app.schemas.report import (
    PeriodReportResponseSchema,
    PremiumHubResponseSchema,
    WeeklyReportResponseSchema,
)
from app.services.report_service import ReportService
from app.utils.datetime import get_seoul_today

router = APIRouter()


@router.get(
    "/monthly/{relationship_id}",
    response_model=SuccessResponseSchema[PeriodReportResponseSchema],
    summary="월간 리포트 조회",
)
def get_monthly_report(
    relationship_id: str,
    current_user: User = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service),
):
    report = report_service.get_period_report(
        current_user=current_user,
        relationship_id=relationship_id,
        today=get_seoul_today(),
        period_type="monthly",
    )
    return success_response(
        data=PeriodReportResponseSchema.model_validate(report),
        message="OK",
    )


@router.get(
    "/yearly/{relationship_id}",
    response_model=SuccessResponseSchema[PeriodReportResponseSchema],
    summary="연간 리포트 조회",
)
def get_yearly_report(
    relationship_id: str,
    current_user: User = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service),
):
    report = report_service.get_period_report(
        current_user=current_user,
        relationship_id=relationship_id,
        today=get_seoul_today(),
        period_type="yearly",
    )
    return success_response(
        data=PeriodReportResponseSchema.model_validate(report),
        message="OK",
    )


@router.get(
    "/premium-hub",
    response_model=SuccessResponseSchema[PremiumHubResponseSchema],
    summary="프리미엄 허브 조회",
)
def get_premium_hub(
    current_user: User = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service),
):
    return success_response(
        data=PremiumHubResponseSchema.model_validate(report_service.get_premium_hub()),
        message="OK",
    )


@router.get(
    "/weekly/{relationship_id}",
    response_model=SuccessResponseSchema[WeeklyReportResponseSchema],
    summary="주간 리포트 조회",
)
def get_weekly_report(
    relationship_id: str,
    current_user: User = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service),
):
    report = report_service.get_weekly_report(
        current_user=current_user,
        relationship_id=relationship_id,
        today=get_seoul_today(),
    )
    return success_response(
        data=WeeklyReportResponseSchema.model_validate(report),
        message="OK",
    )
