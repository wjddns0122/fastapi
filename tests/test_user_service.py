import re

import pytest

from app.core.exceptions import AppException
from app.services.auth_service import AuthService
from app.services.user_service import UserService


def test_user_service_updates_profile_fields(db_session):
    auth_service = AuthService(db=db_session)
    user, _ = auth_service.signup(
        email="user@example.com",
        password="StrongPassword123!",
        nickname="jfh",
    )
    service = UserService(db=db_session)

    updated_user = service.update_profile(
        user=user,
        nickname="new_nickname",
        profile_image_url="https://cdn.example.com/profiles/new.png",
    )

    assert updated_user.nickname == "new_nickname"
    assert updated_user.profile_image_url == "https://cdn.example.com/profiles/new.png"


def test_user_service_creates_profile_image_upload_path(db_session, fake_storage_client):
    auth_service = AuthService(db=db_session)
    user, _ = auth_service.signup(
        email="user@example.com",
        password="StrongPassword123!",
        nickname="jfh",
    )
    service = UserService(db=db_session)

    signed_upload = service.create_profile_image_upload(
        user=user,
        file_name="profile image.png",
        content_type="image/png",
        storage_client=fake_storage_client,
    )

    assert re.match(
        rf"profiles/{user.id}/\d{{8}}-profile-image\.png",
        signed_upload.file_key,
    )
    assert fake_storage_client.calls[0]["content_type"] == "image/png"


def test_user_service_rejects_non_image_content_type(db_session, fake_storage_client):
    auth_service = AuthService(db=db_session)
    user, _ = auth_service.signup(
        email="user@example.com",
        password="StrongPassword123!",
        nickname="jfh",
    )
    service = UserService(db=db_session)

    with pytest.raises(AppException) as exc_info:
        service.create_profile_image_upload(
            user=user,
            file_name="profile.pdf",
            content_type="application/pdf",
            storage_client=fake_storage_client,
        )

    assert exc_info.value.code == "VALIDATION_ERROR"
