def test_create_relationship_returns_pending_relationship(client):
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

    response = client.post(
        "/relationships",
        headers={"Authorization": f"Bearer {requester_access_token}"},
        json={
            "targetUserId": target_user_id,
            "relationshipType": "couple",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "관계 요청이 생성되었습니다."
    assert body["data"]["relationshipType"] == "couple"
    assert body["data"]["status"] == "pending"


def test_accept_relationship_returns_active_relationship(client):
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

    response = client.post(
        f"/relationships/{relationship_id}/accept",
        headers={"Authorization": f"Bearer {target_access_token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "관계 요청이 수락되었습니다."
    assert body["data"]["status"] == "active"


def test_list_my_relationships_returns_partner_information(client):
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
            "nickname": "partner",
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

    response = client.get(
        "/relationships/me",
        headers={"Authorization": f"Bearer {requester_access_token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "OK"
    assert len(body["data"]) == 1
    assert body["data"][0]["relationshipType"] == "couple"
    assert body["data"][0]["status"] == "active"
    assert body["data"][0]["partner"]["nickname"] == "partner"
