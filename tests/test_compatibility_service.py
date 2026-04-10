from datetime import date

import pytest

from app.core.exceptions import AppException
from app.models.relationship_activity import RelationshipActivity
from app.services.auth_service import AuthService
from app.services.behavior_service import BehaviorService
from app.services.compatibility_engine import CompatibilityEngine
from app.services.compatibility_service import CompatibilityService
from app.services.compatibility_text_service import CompatibilityTextService
from app.services.relationship_service import RelationshipService


def _build_service(db_session):
    return CompatibilityService(
        db=db_session,
        behavior_service=BehaviorService(db=db_session),
        compatibility_engine=CompatibilityEngine(),
        compatibility_text_service=CompatibilityTextService(),
    )


def test_compatibility_service_creates_daily_record(db_session):
    auth_service = AuthService(db=db_session)
    requester, _ = auth_service.signup(
        email="requester@example.com",
        password="StrongPassword123!",
        nickname="requester",
    )
    target, _ = auth_service.signup(
        email="target@example.com",
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
    service = _build_service(db_session)

    record = service.get_today_compatibility(
        relationship_id=relationship.id,
        current_user=requester,
        target_date=date(2026, 4, 10),
    )

    assert record.relationship_id == relationship.id
    assert 50 <= record.base_score <= 75
    assert -10 <= record.tarot_score <= 15
    assert -10 <= record.behavior_score <= 15
    assert 0 <= record.final_score <= 100


def test_compatibility_service_returns_same_record_for_same_day(db_session):
    auth_service = AuthService(db=db_session)
    requester, _ = auth_service.signup(
        email="requester@example.com",
        password="StrongPassword123!",
        nickname="requester",
    )
    target, _ = auth_service.signup(
        email="target@example.com",
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
    service = _build_service(db_session)

    first = service.get_today_compatibility(
        relationship_id=relationship.id,
        current_user=requester,
        target_date=date(2026, 4, 10),
    )
    second = service.get_today_compatibility(
        relationship_id=relationship.id,
        current_user=requester,
        target_date=date(2026, 4, 10),
    )

    assert first.id == second.id
    assert first.final_score == second.final_score


def test_compatibility_service_rejects_pending_relationship(db_session):
    auth_service = AuthService(db=db_session)
    requester, _ = auth_service.signup(
        email="requester@example.com",
        password="StrongPassword123!",
        nickname="requester",
    )
    target, _ = auth_service.signup(
        email="target@example.com",
        password="StrongPassword123!",
        nickname="target",
    )
    relationship_service = RelationshipService(db=db_session)
    relationship = relationship_service.create_relationship(
        current_user=requester,
        target_user_id=target.id,
        relationship_type="couple",
    )
    service = _build_service(db_session)

    with pytest.raises(AppException) as exc_info:
        service.get_today_compatibility(
            relationship_id=relationship.id,
            current_user=requester,
            target_date=date(2026, 4, 10),
        )

    assert exc_info.value.code == "CONFLICT"


def test_compatibility_service_scores_recorded_activities(db_session):
    auth_service = AuthService(db=db_session)
    requester, _ = auth_service.signup(
        email="requester@example.com",
        password="StrongPassword123!",
        nickname="requester",
    )
    target, _ = auth_service.signup(
        email="target@example.com",
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
    db_session.add_all(
        [
            RelationshipActivity(
                relationship_id=relationship.id,
                actor_user_id=requester.id,
                event_type="letter_sent",
                occurred_on=date(2026, 4, 10),
                event_metadata={},
            ),
            RelationshipActivity(
                relationship_id=relationship.id,
                actor_user_id=requester.id,
                event_type="shop_visited",
                occurred_on=date(2026, 4, 10),
                event_metadata={},
            ),
            RelationshipActivity(
                relationship_id=relationship.id,
                actor_user_id=requester.id,
                event_type="avatar_changed",
                occurred_on=date(2026, 4, 10),
                event_metadata={},
            ),
            RelationshipActivity(
                relationship_id=relationship.id,
                actor_user_id=requester.id,
                event_type="checkin_completed",
                occurred_on=date(2026, 4, 10),
                event_metadata={},
            ),
            RelationshipActivity(
                relationship_id=relationship.id,
                actor_user_id=target.id,
                event_type="checkin_completed",
                occurred_on=date(2026, 4, 10),
                event_metadata={},
            ),
        ],
    )
    db_session.commit()
    service = _build_service(db_session)

    record = service.get_today_compatibility(
        relationship_id=relationship.id,
        current_user=requester,
        target_date=date(2026, 4, 10),
    )

    assert record.behavior_score > 0
