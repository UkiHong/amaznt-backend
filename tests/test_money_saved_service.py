from decimal import Decimal
from app.services.money_saved_service import calculate_estimated_money_saved


def test_calculate_estimated_money_saved_returns_zero_when_no_saved_reactions():
    estimated_money_saved = calculate_estimated_money_saved(
        saved_my_money_count=0,
        price_paid=Decimal("10.00"),
    )

    assert estimated_money_saved == Decimal("0.00")


def test_calculate_estimated_money_saved_returns_price_paid_for_one_saved_reaction():
    estimated_money_saved = calculate_estimated_money_saved(
        saved_my_money_count=1,
        price_paid=Decimal("10.00"),
    )

    assert estimated_money_saved == Decimal("10.00")


def test_calculate_estimated_money_saved_multiplies_saved_count_by_price_paid():
    estimated_money_saved = calculate_estimated_money_saved(
        saved_my_money_count=5,
        price_paid=Decimal("10.00"),
    )

    assert estimated_money_saved == Decimal("50.00")
