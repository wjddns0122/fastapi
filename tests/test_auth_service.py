import pytest

from app.core.exceptions import AppException
from app.core.security import decode_token
from app.services.auth_service import AuthService


def test_auth_service_signup_persists_user(db_session):
    service = AuthService(db=db_session)

    user, tokens = service.signup(
        email="user@example.com",
        password="StrongPassword123!",
        nickname="jfh",
    )

    assert user.id
    assert user.email == "user@example.com"
    assert tokens["access_token"]
    assert tokens["refresh_token"]


def test_auth_service_login_raises_for_invalid_password(db_session):
    service = AuthService(db=db_session)
    service.signup(
        email="user@example.com",
        password="StrongPassword123!",
        nickname="jfh",
    )

    with pytest.raises(AppException) as exc_info:
        service.login(email="user@example.com", password="WrongPassword123!")

    assert exc_info.value.code == "UNAUTHORIZED"


def test_auth_service_refresh_returns_access_token(db_session):
    service = AuthService(db=db_session)
    user, tokens = service.signup(
        email="user@example.com",
        password="StrongPassword123!",
        nickname="jfh",
    )

    refreshed = service.refresh_access_token(refresh_token=tokens["refresh_token"])
    payload = decode_token(token=refreshed["access_token"], expected_type="access")

    assert payload["sub"] == user.id
