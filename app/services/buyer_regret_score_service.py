from decimal import Decimal
from math import log1p

CALCULATION_VERSION_V1 = "fail_score_v1"
"""
# fail_score_v1:
# value_regret_score = 0.30
# description_mismatch_score = 0.25
# quality_disappointment_score = 0.20
# funniness_score = 0.10
# anger_score = 0.15
"""


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


CALCULATION_VERSION_V2 = "fail_score_v2"
""" 
# positive_validation_count = same_here_count + agree_count
# negative_validation_count = disagree_count

# community_validation_score =
(positive_validation_count + 2) 
/ (positive_validation_count + negative_validation_count + 4) 
* 100

# total_validation_count = same_here_count + agree_count + disagree_count
# community_weight = min(log1p(total_validation_count) / log1p(20) * 0.35, 0.35)

# fail_score_v2 = 
# author_score * (1 - community_weight) + community_validation_score * community_weight
"""

MAX_COMMUNITY_WEIGHT = Decimal("0.35")
COMMUNITY_WEIGHT_TARGET_COUNT = 20


def calculate_community_validation_score(
    same_here_count: int,
    agree_count: int,
    disagree_count: int,
) -> Decimal:
    positive_validation_count = same_here_count + agree_count
    negative_validation_count = disagree_count

    score = (
        Decimal(positive_validation_count + 2)
        / Decimal(positive_validation_count + negative_validation_count + 4)
        * Decimal(100)
    )
    return score.quantize(Decimal("0.01"))


def calculate_community_weight(
    same_here_count: int,
    agree_count: int,
    disagree_count: int,
) -> Decimal:
    total_validation_count = same_here_count + agree_count + disagree_count

    raw_weight = (
        Decimal(str(log1p(total_validation_count)))
        / Decimal(str(log1p(COMMUNITY_WEIGHT_TARGET_COUNT)))
    ) * MAX_COMMUNITY_WEIGHT
    return min(raw_weight, MAX_COMMUNITY_WEIGHT)


def calculate_buyer_regret_score_v2(
    author_score: Decimal,
    same_here_count: int,
    agree_count: int,
    disagree_count: int,
) -> Decimal:
    community_weight = calculate_community_weight(
        same_here_count, agree_count, disagree_count
    )
    community_validation_score = calculate_community_validation_score(
        same_here_count, agree_count, disagree_count
    )

    final_score = (
        author_score * (Decimal(1) - community_weight)
        + community_validation_score * community_weight
    )

    return final_score.quantize(Decimal("0.01"))
