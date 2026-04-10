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


def test_accept_relationship_returns_accepted_relationship(client):
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
    assert body["data"]["status"] == "accepted"


def test_reject_relationship_returns_rejected_relationship(client):
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
            "relationshipType": "friend",
        },
    )
    relationship_id = create_response.json()["data"]["id"]

    response = client.post(
        f"/relationships/{relationship_id}/reject",
        headers={"Authorization": f"Bearer {target_access_token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "관계 요청이 거절되었습니다."
    assert body["data"]["status"] == "rejected"


def test_delete_relationship_removes_relationship(client):
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
            "relationshipType": "friend",
        },
    )
    relationship_id = create_response.json()["data"]["id"]

    response = client.delete(
        f"/relationships/{relationship_id}",
        headers={"Authorization": f"Bearer {requester_access_token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "관계가 삭제되었습니다."


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
    assert body["data"][0]["status"] == "accepted"
    assert body["data"][0]["partner"]["nickname"] == "partner"


def test_list_my_relationships_with_status_filter(client):
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

    client.post(
        "/relationships",
        headers={"Authorization": f"Bearer {requester_access_token}"},
        json={
            "targetUserId": target_user_id,
            "relationshipType": "friend",
        },
    )

    response = client.get(
        "/relationships/me?status=pending",
        headers={"Authorization": f"Bearer {requester_access_token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0]["status"] == "pending"


def test_list_my_relationships_with_direction_filter(client):
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

    client.post(
        "/relationships",
        headers={"Authorization": f"Bearer {requester_access_token}"},
        json={
            "targetUserId": target_user_id,
            "relationshipType": "friend",
        },
    )

    sent_response = client.get(
        "/relationships/me?filter=sent",
        headers={"Authorization": f"Bearer {requester_access_token}"},
    )
    received_response = client.get(
        "/relationships/me?filter=received",
        headers={"Authorization": f"Bearer {target_access_token}"},
    )

    assert sent_response.status_code == 200
    assert len(sent_response.json()["data"]) == 1

    assert received_response.status_code == 200
    assert len(received_response.json()["data"]) == 1
