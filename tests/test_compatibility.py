from unittest.mock import patch

from app.core.config import settings


def _create_accepted_relationship(client):
    requester_signup_response = client.post(
        "/auth/signup",
        json={
            "email": "requester@example.com",
            "password": "StrongPassword123!",
            "nickname": "requester",
        },
    )
    target_signup_response = client.post(
        "/auth/signup",
        json={
            "email": "target@example.com",
            "password": "StrongPassword123!",
            "nickname": "target",
        },
    )
    requester_access_token = requester_signup_response.json()["data"]["tokens"]["accessToken"]
    target_access_token = target_signup_response.json()["data"]["tokens"]["accessToken"]
    target_user_id = target_signup_response.json()["data"]["user"]["id"]

    create_response = client.post(
        "/relationships",
        headers={"Authorization": f"Bearer {requester_access_token}"},
        json={
            "targetUserId": target_user_id,
            "relationshipType": "couple",
        },
    )
    relationship_id = create_response.json()["data"]["id"]

    client.post(
        f"/relationships/{relationship_id}/accept",
        headers={"Authorization": f"Bearer {target_access_token}"},
    )

    return relationship_id, requester_access_token, target_access_token


def test_get_today_compatibility_creates_daily_record(client):
    relationship_id, requester_access_token, _ = _create_accepted_relationship(client)

    response = client.get(
        f"/compatibility/today/{relationship_id}",
        headers={"Authorization": f"Bearer {requester_access_token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "OK"
    assert body["data"]["relationshipId"] == relationship_id
    assert 0 <= body["data"]["finalScore"] <= 100
    assert "summary" in body["data"]
    assert "prescription" in body["data"]


def test_get_today_compatibility_returns_cached_result(client):
    relationship_id, requester_access_token, _ = _create_accepted_relationship(client)

    first_response = client.get(
        f"/compatibility/today/{relationship_id}",
        headers={"Authorization": f"Bearer {requester_access_token}"},
    )
    second_response = client.get(
        f"/compatibility/today/{relationship_id}",
        headers={"Authorization": f"Bearer {requester_access_token}"},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json()["data"] == second_response.json()["data"]


def test_get_today_compatibility_rejects_pending_relationship(client):
    requester_signup_response = client.post(
        "/auth/signup",
        json={
            "email": "requester@example.com",
            "password": "StrongPassword123!",
            "nickname": "requester",
        },
    )
    target_signup_response = client.post(
        "/auth/signup",
        json={
            "email": "target@example.com",
            "password": "StrongPassword123!",
            "nickname": "target",
        },
    )
    requester_access_token = requester_signup_response.json()["data"]["tokens"]["accessToken"]
    target_user_id = target_signup_response.json()["data"]["user"]["id"]

    create_response = client.post(
        "/relationships",
        headers={"Authorization": f"Bearer {requester_access_token}"},
        json={
            "targetUserId": target_user_id,
            "relationshipType": "couple",
        },
    )
    relationship_id = create_response.json()["data"]["id"]

    response = client.get(
        f"/compatibility/today/{relationship_id}",
        headers={"Authorization": f"Bearer {requester_access_token}"},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"


def test_refresh_today_compatibility_requires_internal_token(client):
    relationship_id, requester_access_token, _ = _create_accepted_relationship(client)

    response = client.post(
        f"/compatibility/today/{relationship_id}/refresh",
        headers={"Authorization": f"Bearer {requester_access_token}"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"


def test_refresh_today_compatibility_returns_daily_record(client):
    relationship_id, requester_access_token, _ = _create_accepted_relationship(client)

    test_token = "test-internal-token"
    with patch("app.api.v1.compatibility.settings") as mock_settings:
        mock_settings.compatibility_refresh_token = test_token
        response = client.post(
            f"/compatibility/today/{relationship_id}/refresh",
            headers={
                "Authorization": f"Bearer {requester_access_token}",
                "X-Internal-Token": test_token,
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["relationshipId"] == relationship_id
