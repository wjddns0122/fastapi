from app.api.deps import get_tarot_ai_client


class FakeTarotAIClient:
    def __init__(self) -> None:
        self.calls = []

    def generate_tarot_interpretation(self, prompt):
        self.calls.append(prompt)
        return "오늘은 부드럽게 접근하는 편이 좋습니다. 짧은 안부 메시지가 적합합니다."


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

    return relationship_id, requester_access_token


def test_create_daily_tarot_returns_created_result(client):
    relationship_id, access_token = _create_accepted_relationship(client)
    fake_ai_client = FakeTarotAIClient()
    client.app.dependency_overrides[get_tarot_ai_client] = lambda: fake_ai_client

    response = client.post(
        "/tarot/daily",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "relationshipId": relationship_id,
            "question": "오늘 상대에게 먼저 연락해도 될까?",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "오늘의 타로가 생성되었습니다."
    assert body["data"]["question"] == "오늘 상대에게 먼저 연락해도 될까?"
    assert body["data"]["cardName"]
    assert body["data"]["cardOrientation"] in {"upright", "reversed"}
    assert body["data"]["aiInterpretation"] == (
        "오늘은 부드럽게 접근하는 편이 좋습니다. 짧은 안부 메시지가 적합합니다."
    )
    assert len(fake_ai_client.calls) == 1


def test_create_daily_tarot_reuses_existing_today_result(client):
    relationship_id, access_token = _create_accepted_relationship(client)
    fake_ai_client = FakeTarotAIClient()
    client.app.dependency_overrides[get_tarot_ai_client] = lambda: fake_ai_client

    first_response = client.post(
        "/tarot/daily",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "relationshipId": relationship_id,
            "question": "첫 질문",
        },
    )
    second_response = client.post(
        "/tarot/daily",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "relationshipId": relationship_id,
            "question": "다른 질문",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 200
    assert second_response.json()["message"] == "OK"
    assert second_response.json()["data"] == first_response.json()["data"]
    assert len(fake_ai_client.calls) == 1


def test_list_daily_tarot_history_returns_my_records(client):
    relationship_id, access_token = _create_accepted_relationship(client)
    fake_ai_client = FakeTarotAIClient()
    client.app.dependency_overrides[get_tarot_ai_client] = lambda: fake_ai_client
    client.post(
        "/tarot/daily",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "relationshipId": relationship_id,
            "question": "오늘 상대에게 먼저 연락해도 될까?",
        },
    )

    response = client.get(
        f"/tarot/daily/history?relationshipId={relationship_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "OK"
    assert len(body["data"]) == 1
    assert body["data"][0]["question"] == "오늘 상대에게 먼저 연락해도 될까?"


def test_create_daily_tarot_rejects_pending_relationship(client):
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
    access_token = requester_signup_response.json()["data"]["tokens"]["accessToken"]
    target_user_id = target_signup_response.json()["data"]["user"]["id"]
    create_response = client.post(
        "/relationships",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "targetUserId": target_user_id,
            "relationshipType": "couple",
        },
    )
    relationship_id = create_response.json()["data"]["id"]

    response = client.post(
        "/tarot/daily",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "relationshipId": relationship_id,
            "question": "오늘 상대에게 먼저 연락해도 될까?",
        },
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"
