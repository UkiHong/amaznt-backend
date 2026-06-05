from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel


class RankingPeriod(StrEnum):
    # Allowed period filters for ranking endpoints.
    WEEK = "week"
    MONTH = "month"
    ALL_TIME = "all_time"


class BuyerRegretRankingItem(BaseModel):
    # Basic post data shown in the ranking result.
    post_id: int
    title: str
    product_name: str
    category: str
    price_paid: Decimal
    created_at: datetime

    # author_score is the stored v1 score.
    # buyer_regret_score is the v2 score used for this ranking.
    author_score: Decimal
    buyer_regret_score: Decimal
    calculation_version: str

    # Community validation signals used by Buyer Regret Score v2.
    same_here_count: int
    agree_count: int
    disagree_count: int
    community_validation_count: int


class BuyerRegretRankingResponse(BaseModel):
    # Wrapper response so clients know the period and result count.
    period: RankingPeriod
    rankings: list[BuyerRegretRankingItem]
    count: int


# Wallet Saved Ranking Schemas --------------------------------------------------------
class WalletSavedRankingItem(BaseModel):
    post_id: int
    title: str
    product_name: str
    category: str
    price_paid: Decimal
    currency: str
    created_at: datetime
    estimated_money_saved: Decimal
    saved_my_money_count: int


class WalletSavedRankingResponse(BaseModel):
    rankings: list[WalletSavedRankingItem]
    count: int


class RiskyCategoryRankingItem(BaseModel):
    category: str
    average_buyer_regret_score: Decimal
    post_count: int


class RiskyCategoryRankingResponse(BaseModel):
    rankings: list[RiskyCategoryRankingItem]
    count: int
