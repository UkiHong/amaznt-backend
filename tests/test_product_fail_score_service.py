from decimal import Decimal

from app.services.product_fail_score_service import (
    CALCULATION_VERSION,
    calculate_final_score,
    get_grade,
    normalize_score,
)
import pytest


def test_calculation_version_is_fail_score_v1():
    assert CALCULATION_VERSION == "fail_score_v1"


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
