from datetime import UTC, datetime, timedelta

from app.api.deps import get_storage_client
from app.core.config import settings


class FakeStorageClient:
    def __init__(self) -> None:
        self.calls = []

    def create_signed_upload_url(
        self,
        file_key: str,
        content_type: str,
        upsert: bool = True,
    ):
        self.calls.append(
            {
                "file_key": file_key,
                "content_type": content_type,
                "upsert": upsert,
            },
        )

        class SignedUploadData:
            def __init__(self) -> None:
                self.file_key = file_key
                self.upload_url = f"https://upload.example.com/{file_key}"
                self.public_url = f"https://cdn.example.com/{file_key}"

        return SignedUploadData()


def _create_accepted_relationship(client):
    requester_signup_response = client.post(
        "/auth/signup",
        json={
            "email": "requester-domain@example.com",
            "password": "StrongPassword123!",
            "nickname": "requester",
        },
    )
    target_signup_response = client.post(
        "/auth/signup",
        json={
            "email": "target-domain@example.com",
            "password": "StrongPassword123!",
            "nickname": "target",
        },
    )
    requester_token = requester_signup_response.json()["data"]["tokens"]["accessToken"]
    target_token = target_signup_response.json()["data"]["tokens"]["accessToken"]
    target_user_id = target_signup_response.json()["data"]["user"]["id"]

    create_response = client.post(
        "/relationships",
        headers={"Authorization": f"Bearer {requester_token}"},
        json={
            "targetUserId": target_user_id,
            "relationshipType": "couple",
        },
    )
    relationship_id = create_response.json()["data"]["id"]
    client.post(
        f"/relationships/{relationship_id}/accept",
        headers={"Authorization": f"Bearer {target_token}"},
    )
    return relationship_id, requester_token, target_token, target_user_id


def test_compatibility_today_and_refresh(client):
    relationship_id, requester_token, _, _ = _create_accepted_relationship(client)

    response = client.get(
        f"/compatibility/today/{relationship_id}",
        headers={"Authorization": f"Bearer {requester_token}"},
    )
    refresh_response = client.post(
        f"/compatibility/today/{relationship_id}/refresh",
        headers={"Authorization": f"Bearer {requester_token}"},
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["relationshipId"] == relationship_id
    assert 0 <= response.json()["data"]["finalScore"] <= 100
    assert refresh_response.status_code == 200
    assert refresh_response.json()["message"] == "오늘의 궁합이 재계산되었습니다."


def test_letters_create_list_detail_and_attachment_presign(client):
    relationship_id, requester_token, _, target_user_id = _create_accepted_relationship(client)
    fake_storage_client = FakeStorageClient()
    client.app.dependency_overrides[get_storage_client] = lambda: fake_storage_client

    create_response = client.post(
        "/letters",
        headers={"Authorization": f"Bearer {requester_token}"},
        json={
            "relationshipId": relationship_id,
            "receiverUserId": target_user_id,
            "content": "오늘도 수고했어.",
            "letterType": "scheduled",
            "scheduledAt": (
                datetime.now(UTC) + timedelta(days=1)
            ).isoformat(),
        },
    )
    letter_id = create_response.json()["data"]["id"]
    list_response = client.get(
        "/letters",
        headers={"Authorization": f"Bearer {requester_token}"},
    )
    detail_response = client.get(
        f"/letters/{letter_id}",
        headers={"Authorization": f"Bearer {requester_token}"},
    )
    presign_response = client.post(
        f"/letters/{letter_id}/attachments/presign",
        headers={"Authorization": f"Bearer {requester_token}"},
        json={
            "fileName": "letter-image.jpg",
            "contentType": "image/jpeg",
        },
    )

    assert create_response.status_code == 201
    assert create_response.json()["data"]["status"] == "scheduled"
    assert list_response.status_code == 200
    assert len(list_response.json()["data"]) == 1
    assert detail_response.status_code == 200
    assert detail_response.json()["data"]["content"] == "오늘도 수고했어."
    assert presign_response.status_code == 200
    assert presign_response.json()["data"]["publicUrl"].startswith(
        "https://cdn.example.com/letters/",
    )
    assert len(fake_storage_client.calls) == 1


def test_missions_list_and_complete(client):
    relationship_id, requester_token, _, _ = _create_accepted_relationship(client)

    list_response = client.get(
        "/missions/today",
        headers={"Authorization": f"Bearer {requester_token}"},
    )
    mission_id = list_response.json()["data"][0]["missionId"]
    complete_response = client.post(
        f"/missions/{mission_id}/complete",
        headers={"Authorization": f"Bearer {requester_token}"},
        json={"relationshipId": relationship_id},
    )
    second_list_response = client.get(
        "/missions/today",
        headers={"Authorization": f"Bearer {requester_token}"},
    )

    assert list_response.status_code == 200
    assert complete_response.status_code == 200
    assert complete_response.json()["data"]["status"] == "completed"
    assert second_list_response.json()["data"][0]["status"] == "completed"


def test_weekly_report_returns_generated_report(client):
    relationship_id, requester_token, _, _ = _create_accepted_relationship(client)

    response = client.get(
        f"/reports/weekly/{relationship_id}",
        headers={"Authorization": f"Bearer {requester_token}"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["relationshipId"] == relationship_id
    assert 0 <= response.json()["data"]["averageScore"] <= 100
    assert response.json()["data"]["summary"]


def test_internal_batch_endpoints_require_secret_and_run(client):
    object.__setattr__(settings, "internal_secret", "test-secret")
    relationship_id, requester_token, _, target_user_id = _create_accepted_relationship(client)
    client.post(
        "/letters",
        headers={"Authorization": f"Bearer {requester_token}"},
        json={
            "relationshipId": relationship_id,
            "receiverUserId": target_user_id,
            "content": "곧 도착할 편지",
            "letterType": "scheduled",
            "scheduledAt": (
                datetime.now(UTC) - timedelta(minutes=1)
            ).isoformat(),
        },
    )

    unauthorized_response = client.post("/internal/compatibility/generate-daily")
    compatibility_response = client.post(
        "/internal/compatibility/generate-daily",
        headers={"X-Internal-Secret": "test-secret"},
    )
    letters_response = client.post(
        "/internal/letters/send-scheduled",
        headers={"X-Internal-Secret": "test-secret"},
    )
    reports_response = client.post(
        "/internal/reports/generate-weekly",
        headers={"X-Internal-Secret": "test-secret"},
    )

    assert unauthorized_response.status_code == 401
    assert compatibility_response.status_code == 200
    assert "generatedCount" in compatibility_response.json()["data"]
    assert letters_response.status_code == 200
    assert letters_response.json()["data"]["sentCount"] == 1
    assert reports_response.status_code == 200
    assert "generatedCount" in reports_response.json()["data"]
