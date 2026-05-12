from datetime import date

import pytest

from app.core.exceptions import AppException
from app.services.auth_service import AuthService
from app.services.compatibility_service import CompatibilityService
from app.services.relationship_service import RelationshipService
from app.services.report_service import ReportService


def _create_accepted_relationship(db_session):
    auth_service = AuthService(db=db_session)
    requester, _ = auth_service.signup(
        email="report-requester@example.com",
        password="StrongPassword123!",
        nickname="requester",
    )
    target, _ = auth_service.signup(
        email="report-target@example.com",
        password="StrongPassword123!",
        nickname="target",
    )
    relationship_service = RelationshipService(db=db_session)
    relationship = relationship_service.create_relationship(
        current_user=requester,
        target_user_id=target.id,
        relationship_type="couple",
    )
    relationship_service.accept_relationship(
        relationship_id=relationship.id,
        current_user=target,
    )
    return requester, relationship


def test_report_service_raises_when_week_has_no_compatibility_records(
    db_session,
    monkeypatch,
):
    requester, relationship = _create_accepted_relationship(db_session)
    service = ReportService(db=db_session)

    def do_not_create_daily_compatibility(self, relationship, target_date):
        return None

    monkeypatch.setattr(
        CompatibilityService,
        "ensure_daily_compatibility",
        do_not_create_daily_compatibility,
    )

    with pytest.raises(AppException) as exc_info:
        service.get_weekly_report(
            current_user=requester,
            relationship_id=relationship.id,
            today=date(2026, 4, 10),
        )

    assert exc_info.value.code == "CONFLICT"
    assert exc_info.value.message == "주간 리포트를 생성할 데이터가 없습니다."
