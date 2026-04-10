from app.core.security import create_refresh_token
from app.services.auth_service import AuthService


def test_signup_returns_camel_case_response(client):
    response = client.post(
        "/auth/signup",
        json={
            "email": "user@example.com",
            "password": "StrongPassword123!",
            "nickname": "jfh",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "회원가입이 완료되었습니다."
    assert body["data"]["user"]["email"] == "user@example.com"
    assert body["data"]["tokens"]["accessToken"]
    assert body["data"]["tokens"]["refreshToken"]
    assert body["data"]["tokens"]["tokenType"] == "bearer"


def test_signup_returns_conflict_for_duplicate_email(client):
    payload = {
        "email": "user@example.com",
        "password": "StrongPassword123!",
        "nickname": "jfh",
    }

    client.post("/auth/signup", json=payload)
    response = client.post("/auth/signup", json=payload)

    assert response.status_code == 409
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "CONFLICT"


def test_login_returns_tokens(client):
    signup_payload = {
        "email": "user@example.com",
        "password": "StrongPassword123!",
        "nickname": "jfh",
    }
    client.post("/auth/signup", json=signup_payload)

    response = client.post(
        "/auth/login",
        json={
            "email": "user@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "로그인되었습니다."
    assert body["data"]["tokens"]["tokenType"] == "bearer"


def test_refresh_returns_new_access_token_in_camel_case(client, db_session):
    service = AuthService(db=db_session)
    user, _ = service.signup(
        email="user@example.com",
        password="StrongPassword123!",
        nickname="jfh",
    )
    refresh_token = create_refresh_token(subject=user.id)

    response = client.post(
        "/auth/refresh",
        json={"refreshToken": refresh_token},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["accessToken"]
    assert body["data"]["tokenType"] == "bearer"


def test_me_returns_current_user_profile(client):
    signup_response = client.post(
        "/auth/signup",
        json={
            "email": "user@example.com",
            "password": "StrongPassword123!",
            "nickname": "jfh",
        },
    )
    access_token = signup_response.json()["data"]["tokens"]["accessToken"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["email"] == "user@example.com"
    assert "profileImageUrl" in body["data"]


def test_me_requires_authorization_header(client):
    response = client.get("/auth/me")

    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNAUTHORIZED"
