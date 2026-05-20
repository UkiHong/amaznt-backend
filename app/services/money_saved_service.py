from decimal import Decimal


def calculate_estimated_money_saved(
    saved_my_money_count: int,
    price_paid: Decimal,
) -> Decimal:
    estimated_money_saved = saved_my_money_count * price_paid
    return estimated_money_saved
