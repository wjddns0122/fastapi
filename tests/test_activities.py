import pytest


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


def test_record_relationship_activity_creates_event(client):
    relationship_id, requester_access_token, _ = _create_accepted_relationship(client)

    response = client.post(
        f"/relationships/{relationship_id}/activities",
        headers={"Authorization": f"Bearer {requester_access_token}"},
        json={
            "eventType": "avatar_changed",
            "metadata": {"itemKey": "spring-jacket"},
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "활동이 기록되었습니다."
    assert body["data"]["relationshipId"] == relationship_id
    assert body["data"]["eventType"] == "avatar_changed"


def test_compatibility_reflects_recorded_activities(client):
    relationship_id, requester_access_token, target_access_token = _create_accepted_relationship(client)

    client.post(
        f"/relationships/{relationship_id}/activities",
        headers={"Authorization": f"Bearer {requester_access_token}"},
        json={"eventType": "letter_sent"},
    )
    client.post(
        f"/relationships/{relationship_id}/activities",
        headers={"Authorization": f"Bearer {requester_access_token}"},
        json={"eventType": "shop_visited"},
    )
    client.post(
        f"/relationships/{relationship_id}/activities",
        headers={"Authorization": f"Bearer {requester_access_token}"},
        json={"eventType": "avatar_changed"},
    )
    client.post(
        f"/relationships/{relationship_id}/activities",
        headers={"Authorization": f"Bearer {requester_access_token}"},
        json={"eventType": "checkin_completed"},
    )
    client.post(
        f"/relationships/{relationship_id}/activities",
        headers={"Authorization": f"Bearer {target_access_token}"},
        json={"eventType": "checkin_completed"},
    )
    client.post(
        f"/relationships/{relationship_id}/activities",
        headers={"Authorization": f"Bearer {requester_access_token}"},
        json={"eventType": "couple_item_equipped", "metadata": {"itemKey": "matching-hat"}},
    )
    client.post(
        f"/relationships/{relationship_id}/activities",
        headers={"Authorization": f"Bearer {target_access_token}"},
        json={"eventType": "couple_item_equipped", "metadata": {"itemKey": "matching-hat"}},
    )

    response = client.get(
        f"/compatibility/today/{relationship_id}",
        headers={"Authorization": f"Bearer {requester_access_token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["behaviorScore"] > 0
    assert body["data"]["finalScore"] >= body["data"]["baseScore"]


@pytest.mark.parametrize(
    ("path", "payload", "expected_event_type"),
    [
        ("/shop/visit", {"metadata": {"shopSection": "spring"}}, "shop_visited"),
        ("/avatar/change", {"metadata": {"itemKey": "spring-jacket"}}, "avatar_changed"),
        ("/items/couple/equip", {"metadata": {"itemKey": "matching-hat"}}, "couple_item_equipped"),
        ("/quests/daily/complete", {"metadata": {"questKey": "daily-greeting"}}, "daily_quest_completed"),
        ("/quests/weekly/complete", {"metadata": {"questKey": "weekly-bond"}}, "weekly_quest_completed"),
        ("/checkins", {"metadata": {"mood": "happy"}}, "checkin_completed"),
        ("/letters/send", {"metadata": {"letterId": "uuid"}}, "letter_sent"),
        ("/letters/open", {"metadata": {"letterId": "uuid"}}, "letter_opened"),
    ],
)
def test_specialized_activity_endpoints_record_expected_event(
    client,
    path,
    payload,
    expected_event_type,
):
    relationship_id, requester_access_token, _ = _create_accepted_relationship(client)

    response = client.post(
        f"/relationships/{relationship_id}{path}",
        headers={"Authorization": f"Bearer {requester_access_token}"},
        json=payload,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["eventType"] == expected_event_type
