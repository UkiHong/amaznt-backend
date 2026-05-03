from pydantic import ValidationError
import pytest
import anyio
from app.database import database_engine
from app.schemas.post import PostCreateRequest, PostUpdateRequest

# TestClient is a dummy to send API requests to FastAPI
from fastapi.testclient import TestClient
from app.main import app
import os
from dotenv import load_dotenv


load_dotenv()  # Load environment variables from .env file
ADMIN_EMAIL = os.getenv("TEST_ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("TEST_ADMIN_PASSWORD")
TEST_DUMMY_EMAIL = os.getenv("TEST_DUMMY_EMAIL")
TEST_DUMMY_PASSWORD = os.getenv("TEST_DUMMY_PASSWORD")


# Close/dispose SQLAlchemy async database engine after each test.
# Preventing errors between tests
@pytest.fixture(autouse=True)
def dispose_database_engine_after_test():
    yield
    anyio.run(database_engine.dispose)


# token function for use in post tests.
# Use for tests when authorized user is required.
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


def test_create_post_without_token_returns_401():
    with TestClient(app) as client:
        response = client.post(
            "/posts",
            json={
                "title": "Test Post",
                "product_name": "Test Product",
                "price_paid": 19.99,
                "fail_reason": "It broke after one use",
                "platform": "Amazon",
                "category": "Electronics",
                "value_regret_score": 4,
                "description_mismatch_score": 3,
                "quality_disappointment_score": 2,
                "funniness_score": 5,
                "anger_score": 1,
            },
        )
    assert response.status_code == 401


def create_test_post(client: TestClient, headers: dict) -> int:
    response = client.post(
        "/posts",
        headers=headers,
        json={
            "title": "Test Post with Token",
            "product_name": "Test Product",
            "price_paid": 19.99,
            "fail_reason": "It broke after one use",
            "platform": "Amazon",
            "category": "Electronics",
            "value_regret_score": 4,
            "description_mismatch_score": 3,
            "quality_disappointment_score": 2,
            "funniness_score": 5,
            "anger_score": 1,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_create_post_with_token_returns_201():
    with TestClient(app) as client:
        auth_headers = make_auth_headers(client)
        # dummy_headers = make_auth_headers(client, TEST_DUMMY_EMAIL, TEST_DUMMY_PASSWORD)
        post_id = create_test_post(client, auth_headers)
        assert post_id is not None


def test_get_posts_returns_200():
    with TestClient(app) as client:
        response = client.get("/posts")
    assert response.status_code == 200

    assert "posts" in response.json()
    assert "count" in response.json()
    assert "page" in response.json()
    assert "page_size" in response.json()


def test_get_post_returns_created_post():
    pass


def test_get_missing_post_returns_404():
    with TestClient(app) as client:
        response = client.get("/posts/999999")

    assert response.status_code == 404


def test_post_create_request_rejects_scores_outside_1_to_5():
    with pytest.raises(ValidationError):
        PostCreateRequest(
            title="Test Post",
            product_name="Test Product",
            price_paid=19.99,
            fail_reason="It broke after one use",
            platform="Amazon",
            category="Electronics",
            value_regret_score=0,  # Invalid score
            description_mismatch_score=3,
            quality_disappointment_score=4,
            funniness_score=5,
            anger_score=2,
        )


# PostUpdateRequest schema tests.
def test_post_update_request_allows_partial_update():
    request = PostUpdateRequest(title="Updated title")

    assert request.title == "Updated title"
    assert request.product_name is None
    assert request.anger_score is None


# Comment test --------------------------------------------------
