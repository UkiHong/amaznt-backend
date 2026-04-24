from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_success():
    pass


# Test for /me endpoint


def test_me_without_token_returns_401():
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_login_with_wrong_credentials_returns_401():
    response = client.post(
        "/auth/login",
        data={
            "username": "not-existing-user@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401


def test_me_returns_current_active_user():
    pass


def test_me_without_token_returns_401():
    pass


def test_me_with_inactive_user_returns_403():
    pass


#############################
