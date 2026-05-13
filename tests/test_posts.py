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


# Helper function to create a test post.
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


def test_get_post_detail_includes_images():
    with TestClient(app) as client:
        auth_headers = make_auth_headers(client)
        post_id = create_test_post(client, auth_headers)
        image_id = create_test_image(client, post_id, auth_headers)

        response = client.get(f"/posts/{post_id}")

    assert response.status_code == 200

    response_data = response.json()
    images = response_data["images"]
    image_ids = []
    for image in images:
        image_ids.append(image["id"])
    assert image_id in image_ids


@pytest.mark.skip(reason="TODO: implement post detail response test")
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
def create_test_comment(client: TestClient, post_id: int, headers: dict) -> int:
    response = client.post(
        f"/posts/{post_id}/comments",
        headers=headers,
        json={
            "content": "Test Comment by Dummy",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_delete_comment_with_token_returns_204():
    with TestClient(app) as client:
        auth_headers = make_auth_headers(client)
        # dummy_headers = make_auth_headers(client, TEST_DUMMY_EMAIL, TEST_DUMMY_PASSWORD)
        post_id = create_test_post(client, auth_headers)
        comment_id = create_test_comment(client, post_id, auth_headers)

        response = client.delete(
            f"/posts/{post_id}/comments/{comment_id}",
            headers=auth_headers,
        )

    assert response.status_code == 204


def test_delete_comment_by_non_author_returns_403():
    with TestClient(app) as client:
        auth_headers = make_auth_headers(client)
        dummy_headers = make_auth_headers(client, TEST_DUMMY_EMAIL, TEST_DUMMY_PASSWORD)
        post_id = create_test_post(client, auth_headers)
        comment_id = create_test_comment(client, post_id, auth_headers)

        response = client.delete(
            f"/posts/{post_id}/comments/{comment_id}",
            headers=dummy_headers,
        )

    assert response.status_code == 403


# Image test --------------------------------------------------
# Helper function for creating a test image.
def create_test_image(client: TestClient, post_id: int, headers: dict) -> int:
    response = client.post(
        f"/posts/{post_id}/images",
        headers=headers,
        files={
            "file": (
                "test.png",
                b"fake image bytes",
                "image/png",
            ),
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_delete_image_with_token_returns_204():
    with TestClient(app) as client:
        auth_headers = make_auth_headers(client)
        post_id = create_test_post(client, auth_headers)
        image_id = create_test_image(client, post_id, auth_headers)

        response = client.delete(
            f"/posts/{post_id}/images/{image_id}",
            headers=auth_headers,
        )
    assert response.status_code == 204


def test_delete_image_by_non_author_returns_403():
    with TestClient(app) as client:
        auth_headers = make_auth_headers(client)
        dummy_headers = make_auth_headers(client, TEST_DUMMY_EMAIL, TEST_DUMMY_PASSWORD)
        post_id = create_test_post(client, auth_headers)
        image_id = create_test_image(client, post_id, auth_headers)

        response = client.delete(
            f"/posts/{post_id}/images/{image_id}",
            headers=dummy_headers,
        )

    assert response.status_code == 403


# Reaction Test ----------------------------------------------------------------


# # Helper def when user request to react to a post
def react_to_post(client: TestClient, post_id: int, headers: dict, reaction_type: str):
    return client.post(
        f"/posts/{post_id}/reactions/{reaction_type}",
        headers=headers,
    )


def test_same_reaction_toggles_off():
    with TestClient(app) as client:
        author_headers = make_auth_headers(client)
        reactor_headers = make_auth_headers(
            client,
            TEST_DUMMY_EMAIL,
            TEST_DUMMY_PASSWORD,
        )
        post_id = create_test_post(client, author_headers)

        first_response = react_to_post(
            client,
            post_id,
            reactor_headers,
            "HELPFUL",
        )

        second_response = react_to_post(
            client,
            post_id,
            reactor_headers,
            "HELPFUL",
        )

        assert first_response.status_code == 200
        assert first_response.json()["status"] == "created"
        assert first_response.json()["reaction_type"] == "HELPFUL"

        assert second_response.status_code == 200
        assert second_response.json()["status"] == "deleted"
        assert second_response.json()["reaction_type"] is None


def test_different_reaction_updates_existing_reaction():
    with TestClient(app) as client:
        author_headers = make_auth_headers(client)
        reactor_headers = make_auth_headers(
            client,
            TEST_DUMMY_EMAIL,
            TEST_DUMMY_PASSWORD,
        )
        post_id = create_test_post(client, author_headers)

        first_response = react_to_post(
            client,
            post_id,
            reactor_headers,
            "HELPFUL",
        )

        second_response = react_to_post(
            client,
            post_id,
            reactor_headers,
            "SAME_HERE",
        )

        assert first_response.status_code == 200
        assert first_response.json()["status"] == "created"
        assert first_response.json()["reaction_type"] == "HELPFUL"

        assert second_response.status_code == 200
        assert second_response.json()["status"] == "updated"
        assert second_response.json()["reaction_type"] == "SAME_HERE"


def test_author_cannot_react_to_own_post():
    with TestClient(app) as client:
        author_headers = make_auth_headers(client)

        post_id = create_test_post(client, author_headers)

        my_reaction = react_to_post(
            client,
            post_id,
            author_headers,
            "HELPFUL",
        )

        assert my_reaction.status_code == 403


def test_post_detail_includes_reaction_summary_for_anonymous_user():
    with TestClient(app) as client:
        author_headers = make_auth_headers(client)

        post_id = create_test_post(client, author_headers)

        # A different user reacts to the post.
        reactor_headers = make_auth_headers(
            client,
            TEST_DUMMY_EMAIL,
            TEST_DUMMY_PASSWORD,
        )

        # Anonymous users can still read post detail.
        # No Authorization header is sent here.
        react_to_post(
            client,
            post_id,
            reactor_headers,
            reaction_type="HELPFUL",
        )

        response = client.get(f"/posts/{post_id}")

        assert response.status_code == 200

        response_data = response.json()
        reaction_summary = response_data["reaction_summary"]

        # Reaction summary is public aggregate data.
        assert reaction_summary["helpful_count"] == 1
        assert reaction_summary["same_here_count"] == 0
        assert reaction_summary["saved_my_money_count"] == 0

        # Anonymous users do not have a personal reaction state.
        assert response_data["my_reaction"] is None


def test_post_detail_includes_my_reaction_for_logged_in_user():
    with TestClient(app) as client:
        author_headers = make_auth_headers(client)
        post_id = create_test_post(client, author_headers)

        # This user will check if my_reaction shows when getting the post
        reactor_headers = make_auth_headers(
            client,
            TEST_DUMMY_EMAIL,
            TEST_DUMMY_PASSWORD,
        )

        react_response = react_to_post(
            client,
            post_id,
            reactor_headers,
            "SAME_HERE",
        )
        assert react_response.status_code == 200

        response = client.get(
            f"/posts/{post_id}",
            headers=reactor_headers,
        )
        assert response.status_code == 200

        response_data = response.json()
        reaction_summary = response_data["reaction_summary"]

        assert response_data["my_reaction"] == "SAME_HERE"
        assert reaction_summary["same_here_count"] == 1
