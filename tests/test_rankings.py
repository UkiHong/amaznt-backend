import anyio
import pytest

from app.database import database_engine

from starlette.testclient import TestClient
from app.main import app

from tests.test_posts import ADMIN_EMAIL, ADMIN_PASSWORD


@pytest.fixture(autouse=True)
def dispose_database_engine_after_test():
    yield
    anyio.run(database_engine.dispose)


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


def create_ranking_test_post(
    client: TestClient,
    headers: dict,
    title: str,
    value_regret_score: int,
    description_mismatch_score: int,
    quality_disappointment_score: int,
    funniness_score: int,
    anger_score: int,
) -> int:
    response = client.post(
        "/posts",
        headers=headers,
        json={
            "title": title,
            "product_name": "Test Product",
            "price_paid": 19.99,
            "fail_reason": "It broke after one use",
            "platform": "Amazon",
            "category": "electronics",
            "value_regret_score": value_regret_score,
            "description_mismatch_score": description_mismatch_score,
            "quality_disappointment_score": quality_disappointment_score,
            "funniness_score": funniness_score,
            "anger_score": anger_score,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_buyer_regret_ranking_rejects_invalid_period():
    with TestClient(app) as client:
        response = client.get("/rankings/buyer-regret?period=invalid_period")

    assert response.status_code == 422


def test_buyer_regret_ranking_returns_response_shape():
    with TestClient(app) as client:
        response = client.get("/rankings/buyer-regret")

    assert response.status_code == 200

    response_data = response.json()
    assert response_data["period"] == "week"
    assert "rankings" in response_data
    assert "count" in response_data
    assert isinstance(response_data["rankings"], list)


def test_buyer_regret_ranking_orders_posts_by_buyer_regret_score():
    with TestClient(app) as client:
        headers = make_auth_headers(client)

        low_score_post_id = create_ranking_test_post(
            client, headers, "Low Score Post", 1, 2, 3, 4, 5
        )

        high_score_post_id = create_ranking_test_post(
            client, headers, "High Score Post", 5, 5, 5, 5, 5
        )

        response = client.get("/rankings/buyer-regret?period=all_time&limit=100")

    assert response.status_code == 200

    rankings = response.json()["rankings"]

    assert rankings[0]["post_id"] == high_score_post_id
    assert rankings[0]["buyer_regret_score"] == "100.00"
