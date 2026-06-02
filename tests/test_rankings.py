from starlette.testclient import TestClient
from app.main import app

from tests.test_posts import ADMIN_EMAIL, ADMIN_PASSWORD


def make_auth_headers(
    client: TestClient, email: str = ADMIN_EMAIL, password: str = ADMIN_PASSWORD
) -> dict:
    login_response = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert login_response.status_code == 200
    access_token = login_response.json().get("access_token")
    assert access_token is not None

    return {"Authorization": f"Bearer {access_token}"}


def test_buyer_regret_ranking_rejects_invalid_period():
    with TestClient(app) as client:
        response = client.get("/rankings/buyer-regret?period=invalid_period")

    assert response.status_code == 422
