def _signup(client, email: str, nickname: str) -> tuple[str, str]:
    response = client.post(
        "/auth/signup",
        json={
            "email": email,
            "password": "StrongPassword123!",
            "nickname": nickname,
        },
    )
    body = response.json()
    return body["data"]["tokens"]["accessToken"], body["data"]["user"]["id"]


def _create_accepted_relationship(client, prefix: str = "mvp") -> tuple[str, str, str]:
    requester_token, _ = _signup(
        client,
        email=f"requester-{prefix}@example.com",
        nickname="requester",
    )
    target_token, target_user_id = _signup(
        client,
        email=f"target-{prefix}@example.com",
        nickname="target",
    )
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
    return relationship_id, requester_token, target_token


def test_home_today_returns_mvp_screen_payload(client):
    relationship_id, requester_token, _ = _create_accepted_relationship(client)

    response = client.get(
        "/home/today",
        headers={"Authorization": f"Bearer {requester_token}"},
        params={"relationshipId": relationship_id},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["relationshipId"] == relationship_id
    assert len(body["data"]["keywords"]) == 3
    assert "compatibility" in body["data"]
    assert "tarotPreview" in body["data"]
    assert len(body["data"]["missions"]) >= 1
    assert body["data"]["letterCta"]["action"] == "write_letter"
    assert len(body["data"]["recentScores"]) == 7


def test_relationship_invitation_flow_connects_target_user(client):
    requester_token, _ = _signup(
        client,
        email="invite-requester@example.com",
        nickname="requester",
    )
    target_token, _ = _signup(
        client,
        email="invite-target@example.com",
        nickname="target",
    )

    invitation_response = client.post(
        "/relationships/invitations",
        headers={"Authorization": f"Bearer {requester_token}"},
        json={"relationshipType": "couple"},
    )
    token = invitation_response.json()["data"]["token"]
    accept_response = client.post(
        f"/relationships/invitations/{token}/accept",
        headers={"Authorization": f"Bearer {target_token}"},
    )

    assert invitation_response.status_code == 201
    assert invitation_response.json()["data"]["inviteUrl"].endswith(token)
    assert accept_response.status_code == 200
    assert accept_response.json()["data"]["status"] == "accepted"


def test_relationship_invitation_accepts_existing_pending_relationship(client):
    requester_token, _ = _signup(
        client,
        email="invite-pending-requester@example.com",
        nickname="requester",
    )
    target_token, target_user_id = _signup(
        client,
        email="invite-pending-target@example.com",
        nickname="target",
    )
    create_response = client.post(
        "/relationships",
        headers={"Authorization": f"Bearer {requester_token}"},
        json={
            "targetUserId": target_user_id,
            "relationshipType": "couple",
        },
    )
    pending_relationship_id = create_response.json()["data"]["id"]
    invitation_response = client.post(
        "/relationships/invitations",
        headers={"Authorization": f"Bearer {requester_token}"},
        json={"relationshipType": "couple"},
    )
    token = invitation_response.json()["data"]["token"]

    accept_response = client.post(
        f"/relationships/invitations/{token}/accept",
        headers={"Authorization": f"Bearer {target_token}"},
    )

    assert accept_response.status_code == 200
    assert accept_response.json()["data"]["id"] == pending_relationship_id
    assert accept_response.json()["data"]["status"] == "accepted"


def test_solo_relationship_allows_onboarding_without_partner(client):
    access_token, _ = _signup(
        client,
        email="solo@example.com",
        nickname="solo",
    )

    response = client.post(
        "/relationships/solo",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"relationshipType": "friend"},
    )

    assert response.status_code == 201
    assert response.json()["data"]["status"] == "accepted"


def test_letter_draft_conditional_and_templates(client):
    relationship_id, requester_token, target_token = _create_accepted_relationship(
        client,
        prefix="letter-gap",
    )
    target_profile = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {target_token}"},
    ).json()["data"]

    draft_response = client.post(
        "/letters",
        headers={"Authorization": f"Bearer {requester_token}"},
        json={
            "relationshipId": relationship_id,
            "receiverUserId": target_profile["id"],
            "content": "나중에 다듬을 편지",
            "letterType": "draft",
        },
    )
    conditional_response = client.post(
        "/letters",
        headers={"Authorization": f"Bearer {requester_token}"},
        json={
            "relationshipId": relationship_id,
            "receiverUserId": target_profile["id"],
            "content": "힘들 때 열어봐.",
            "letterType": "conditional",
            "conditionType": "receiver_mood_low",
        },
    )
    templates_response = client.get(
        "/letters/templates",
        headers={"Authorization": f"Bearer {requester_token}"},
    )

    assert draft_response.status_code == 201
    assert draft_response.json()["data"]["status"] == "draft"
    assert conditional_response.status_code == 201
    assert conditional_response.json()["data"]["status"] == "conditional_pending"
    assert templates_response.status_code == 200
    assert len(templates_response.json()["data"]) >= 4


def test_reward_profile_reflects_mission_completion(client):
    relationship_id, requester_token, _ = _create_accepted_relationship(
        client,
        prefix="reward-gap",
    )
    missions_response = client.get(
        "/missions/today",
        headers={"Authorization": f"Bearer {requester_token}"},
        params={"relationshipId": relationship_id},
    )
    mission_id = missions_response.json()["data"][0]["missionId"]
    client.post(
        f"/missions/{mission_id}/complete",
        headers={"Authorization": f"Bearer {requester_token}"},
        json={"relationshipId": relationship_id},
    )

    response = client.get(
        f"/rewards/relationships/{relationship_id}",
        headers={"Authorization": f"Bearer {requester_token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["relationshipId"] == relationship_id
    assert body["data"]["points"] >= 10
    assert body["data"]["experience"] >= 10
    assert body["data"]["level"] >= 1


def test_monthly_yearly_reports_and_premium_hub(client):
    relationship_id, requester_token, _ = _create_accepted_relationship(
        client,
        prefix="report-gap",
    )
    client.get(
        f"/compatibility/today/{relationship_id}",
        headers={"Authorization": f"Bearer {requester_token}"},
    )

    monthly_response = client.get(
        f"/reports/monthly/{relationship_id}",
        headers={"Authorization": f"Bearer {requester_token}"},
    )
    yearly_response = client.get(
        f"/reports/yearly/{relationship_id}",
        headers={"Authorization": f"Bearer {requester_token}"},
    )
    premium_response = client.get(
        "/reports/premium-hub",
        headers={"Authorization": f"Bearer {requester_token}"},
    )

    assert monthly_response.status_code == 200
    assert monthly_response.json()["data"]["periodType"] == "monthly"
    assert yearly_response.status_code == 200
    assert yearly_response.json()["data"]["periodType"] == "yearly"
    assert premium_response.status_code == 200
    assert "monthly_report" in premium_response.json()["data"]["paidFeatures"]
