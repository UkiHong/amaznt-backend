import pytest
from app.services.confidence_score_service import calculate_confidence_score

SAME_HERE_TARGET_COUNT = 20
SAME_HERE_MAX_SCORE = 40

HELPFUL_TARGET_COUNT = 30
HELPFUL_MAX_SCORE = 30

COMMENT_TARGET_COUNT = 20
COMMENT_MAX_SCORE = 20

IMAGE_TARGET_COUNT = 5
IMAGE_MAX_SCORE = 10


def test_calculate_confidence_score_returns_zero_when_no_signals():
    score = calculate_confidence_score(
        helpful_count=0,
        same_here_count=0,
        comment_count=0,
        image_count=0,
    )

    assert score == 0.0


def test_calculate_confidence_score_returns_100_when_all_targets_are_met():
    score = calculate_confidence_score(
        helpful_count=30,
        same_here_count=20,
        comment_count=20,
        image_count=5,
    )

    assert score == 100.0


def test_calculate_confidence_score_does_not_exceed_100_when_counts_are_high():
    score = calculate_confidence_score(
        helpful_count=999,
        same_here_count=999,
        comment_count=999,
        image_count=999,
    )

    assert score == 100.0


def test_calculate_confidence_score_returns_67():
    score = calculate_confidence_score(
        helpful_count=5,
        same_here_count=10,
        comment_count=15,
        image_count=1,
    )

    assert score == 67.4
