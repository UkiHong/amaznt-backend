from decimal import Decimal

from app.services.buyer_regret_score_service import (
    CALCULATION_VERSION_V1,
    calculate_buyer_regret_score_v2,
    calculate_community_validation_score,
    calculate_community_weight,
    calculate_final_score,
    get_grade,
    normalize_score,
)
import pytest


# Buyer Regret Score V1 tests--------------------------------------------
def test_calculation_version_is_fail_score_v1():
    assert CALCULATION_VERSION_V1 == "fail_score_v1"


def test_normalize_score_returns_20_for_1():
    assert normalize_score(1) == 20


def test_normalize_score_returns_100_for_5():
    assert normalize_score(5) == 100


def test_normalize_score_raises_value_error_for_invalid_score():
    with pytest.raises(ValueError):
        normalize_score(0)

    with pytest.raises(ValueError):
        normalize_score(6)


def test_calculate_final_score_returns_expected_weighted_score():
    assert calculate_final_score(1, 1, 1, 1, 1) == Decimal("20.00")
    assert calculate_final_score(5, 5, 5, 5, 5) == Decimal("100.00")
    assert calculate_final_score(3, 4, 2, 5, 1) == Decimal("59.00")


def test_get_grade_returns_expected_boundary_grades():
    assert get_grade(20) == "Level 1 - Somehow Fine"
    assert get_grade(40) == "Level 2 - Mild Regret"
    assert get_grade(60) == "Level 3 - Wallet Bruised"
    assert get_grade(80) == "Level 4 - Proper Letdown"
    assert get_grade(95) == "Level 5 - Absolute Rubbish"
    assert get_grade(100) == "Level 6 - Hall of Shame"


# Buyer Regret Score V2 tests--------------------------------------------


# Community Validation Score tests
def test_community_validation_score_returns_50_without_validation():
    assert calculate_community_validation_score(0, 0, 0) == Decimal("50.00")


def test_community_validation_score_increases_with_positive_validation():
    assert calculate_community_validation_score(1, 0, 0) == Decimal("60.00")


def test_community_validation_score_decreases_with_negative_validation():
    assert calculate_community_validation_score(0, 0, 1) == Decimal("40.00")


# Community Weight tests
def test_community_weight_returns_zero_without_validation():
    assert calculate_community_weight(0, 0, 0) == Decimal("0.00")


def test_community_weight_does_not_exceed_max_weight():
    assert calculate_community_weight(999, 999, 999) == Decimal("0.35")


# Final score V2 tests
def test_buyer_regret_score_v2_returns_author_score_without_validation():
    score = calculate_buyer_regret_score_v2(
        author_score=80,
        same_here_count=0,
        agree_count=0,
        disagree_count=0,
    )
    assert score == Decimal("80.00")
