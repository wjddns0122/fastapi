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

    assert accepted_relationship.status == "accepted"


def test_relationship_service_rejects_pending_relationship(db_session):
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
        relationship_type="friend",
    )

    rejected_relationship = service.reject_relationship(
        relationship_id=relationship.id,
        current_user=target,
    )

    assert rejected_relationship.status == "rejected"


def test_relationship_service_deletes_relationship(db_session):
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
        relationship_type="friend",
    )

    service.delete_relationship(
        relationship_id=relationship.id,
        current_user=requester,
    )

    assert service.get_relationship_by_id(relationship_id=relationship.id) is None


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


def test_relationship_service_list_filters_by_status(db_session):
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
        relationship_type="friend",
    )

    pending_list = service.list_my_relationships(current_user=requester, status="pending")
    accepted_list = service.list_my_relationships(current_user=requester, status="accepted")

    assert len(pending_list) == 1
    assert len(accepted_list) == 0


def test_relationship_service_list_filters_by_direction(db_session):
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
        relationship_type="friend",
    )

    sent_list = service.list_my_relationships(current_user=requester, filter="sent")
    received_list = service.list_my_relationships(current_user=target, filter="received")
    requester_received = service.list_my_relationships(current_user=requester, filter="received")

    assert len(sent_list) == 1
    assert len(received_list) == 1
    assert len(requester_received) == 0
