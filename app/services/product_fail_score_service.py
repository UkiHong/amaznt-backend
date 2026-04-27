from decimal import Decimal

# fail_score_v1:
# value_regret_score = 0.30
# description_mismatch_score = 0.25
# quality_disappointment_score = 0.20
# funniness_score = 0.10
# anger_score = 0.15
CALCULATION_VERSION = "fail_score_v1"


def normalize_score(value: int) -> int:
    if value < 1 or value > 5:
        raise ValueError("Score must be between 1 and 5")

    return value * 20


def calculate_final_score(
    value_regret_score: int,
    description_mismatch_score: int,
    quality_disappointment_score: int,
    funniness_score: int,
    anger_score: int,
) -> Decimal:
    value_regret_score = normalize_score(value_regret_score)
    description_mismatch_score = normalize_score(description_mismatch_score)
    quality_disappointment_score = normalize_score(quality_disappointment_score)
    funniness_score = normalize_score(funniness_score)
    anger_score = normalize_score(anger_score)

    final_score = (
        Decimal(value_regret_score) * Decimal("0.30")
        + Decimal(description_mismatch_score) * Decimal("0.25")
        + Decimal(quality_disappointment_score) * Decimal("0.20")
        + Decimal(funniness_score) * Decimal("0.10")
        + Decimal(anger_score) * Decimal("0.15")
    )

    return final_score.quantize(Decimal("0.01"))


def get_grade(final_score: Decimal) -> str:
    if final_score <= 20:
        return "Level 1 - Somehow Fine"
    if final_score <= 40:
        return "Level 2 - Mild Regret"
    if final_score <= 60:
        return "Level 3 - Wallet Bruised"
    if final_score <= 80:
        return "Level 4 - Proper Letdown"
    if final_score <= 95:
        return "Level 5 - Absolute Rubbish"
    return "Level 6 - Hall of Shame"
