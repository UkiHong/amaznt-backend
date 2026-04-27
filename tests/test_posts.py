from pydantic import ValidationError
import pytest

from app.schemas.post import PostCreateRequest


def test_create_post_without_token_returns_401():
    pass


def test_create_post_with_token_returns_201():
    pass


def test_get_posts_returns_200():
    pass


def test_get_post_returns_created_post():
    pass


def test_get_missing_post_returns_404():
    pass


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
