from app.api.deps import get_storage_client


def test_update_me_updates_profile(client):
    signup_response = client.post(
        "/auth/signup",
        json={
            "email": "user@example.com",
            "password": "StrongPassword123!",
            "nickname": "jfh",
        },
    )
    access_token = signup_response.json()["data"]["tokens"]["accessToken"]

    response = client.patch(
        "/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "nickname": "new_nickname",
            "profileImageUrl": "https://cdn.example.com/profiles/new.png",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "프로필이 수정되었습니다."
    assert body["data"]["nickname"] == "new_nickname"
    assert body["data"]["profileImageUrl"] == "https://cdn.example.com/profiles/new.png"


def test_update_me_requires_body_fields(client):
    signup_response = client.post(
        "/auth/signup",
        json={
            "email": "user@example.com",
            "password": "StrongPassword123!",
            "nickname": "jfh",
        },
    )
    access_token = signup_response.json()["data"]["tokens"]["accessToken"]

    response = client.patch(
        "/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
        json={},
    )

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_profile_image_presign_returns_signed_upload_data(
    client,
    fake_storage_client,
):
    signup_response = client.post(
        "/auth/signup",
        json={
            "email": "user@example.com",
            "password": "StrongPassword123!",
            "nickname": "jfh",
        },
    )
    access_token = signup_response.json()["data"]["tokens"]["accessToken"]

    client.app.dependency_overrides[get_storage_client] = lambda: fake_storage_client
    response = client.post(
        "/users/me/profile-image/presign",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "fileName": "profile.png",
            "contentType": "image/png",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "업로드 URL이 발급되었습니다."
    assert body["data"]["fileKey"].endswith("-profile.png")
    assert body["data"]["uploadUrl"].startswith("https://upload.example.com/")
    assert body["data"]["publicUrl"].startswith("https://cdn.example.com/")


def test_profile_image_presign_rejects_non_image_type(
    client,
    fake_storage_client,
):
    signup_response = client.post(
        "/auth/signup",
        json={
            "email": "user@example.com",
            "password": "StrongPassword123!",
            "nickname": "jfh",
        },
    )
    access_token = signup_response.json()["data"]["tokens"]["accessToken"]

    client.app.dependency_overrides[get_storage_client] = lambda: fake_storage_client
    response = client.post(
        "/users/me/profile-image/presign",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "fileName": "profile.pdf",
            "contentType": "application/pdf",
        },
    )

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
