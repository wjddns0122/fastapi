import pytest

from app.core.exceptions import AppException
from app.services.auth_service import AuthService
from app.services.relationship_service import RelationshipService


def test_relationship_service_creates_pending_relationship(db_session):
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
    service = RelationshipService(db=db_session)

    relationship = service.create_relationship(
        current_user=requester,
        target_user_id=target.id,
        relationship_type="couple",
    )

    assert relationship.id
    assert relationship.relationship_type == "couple"
    assert relationship.status == "pending"


def test_relationship_service_accepts_pending_relationship(db_session):
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
    service = RelationshipService(db=db_session)
    relationship = service.create_relationship(
        current_user=requester,
        target_user_id=target.id,
        relationship_type="couple",
    )

    accepted_relationship = service.accept_relationship(
        relationship_id=relationship.id,
        current_user=target,
    )

    assert accepted_relationship.status == "active"


def test_relationship_service_rejects_duplicate_relationship(db_session):
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
    service = RelationshipService(db=db_session)
    service.create_relationship(
        current_user=requester,
        target_user_id=target.id,
        relationship_type="couple",
    )

    with pytest.raises(AppException) as exc_info:
        service.create_relationship(
            current_user=requester,
            target_user_id=target.id,
            relationship_type="friend",
        )

    assert exc_info.value.code == "CONFLICT"
