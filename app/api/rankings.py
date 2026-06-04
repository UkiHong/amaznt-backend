from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select

from app.database import get_db_session
from app.models.post import Post, ProductFailScore
from app.models.reaction import PostReaction, ReactionType
from app.models.verdict import PostVerdict, VerdictType
from app.schemas.ranking import (
    RankingPeriod,
    BuyerRegretRankingItem,
    BuyerRegretRankingResponse,
    WalletSavedRankingItem,
    WalletSavedRankingResponse,
)

from app.services.buyer_regret_score_service import (
    CALCULATION_VERSION_V2,
    calculate_buyer_regret_score_v2,
)

router = APIRouter(
    prefix="/rankings",
    tags=["rankings"],
)


def get_period_start(period: RankingPeriod) -> datetime | None:
    # Convert a ranking period into a created_at cutoff for the DB query.
    # all_time returns None because it should not filter by created_at.
    now = datetime.now(timezone.utc)

    if period == RankingPeriod.WEEK:
        return now - timedelta(days=7)

    if period == RankingPeriod.MONTH:
        return now - timedelta(days=30)

    return None


@router.get("/buyer-regret", response_model=BuyerRegretRankingResponse)
async def get_buyer_regret_ranking(
    period: RankingPeriod = Query(RankingPeriod.WEEK),
    limit: int = Query(10, ge=1, le=100),
    db=Depends(get_db_session),
):
    period_start = get_period_start(period)

    # Start from posts because rankings display post data.
    # Join ProductFailScore because the v1 author score lives there.
    query = (
        select(Post, ProductFailScore)
        .select_from(Post)
        .join(ProductFailScore, ProductFailScore.post_id == Post.id)
    )

    # week/month rankings only include recent posts.
    # all_time skips this filter because period_start is None.
    if period_start is not None:
        query = query.where(Post.created_at >= period_start)

    result = await db.execute(query)
    rows = result.all()

    ranking_items = []

    for post, score in rows:
        # SAME_HERE is a reaction signal used by Buyer Regret Score v2.
        same_here_count_result = await db.execute(
            select(func.count(PostReaction.id)).where(
                PostReaction.post_id == post.id,
                PostReaction.reaction_type == ReactionType.SAME_HERE,
            )
        )
        same_here_count = same_here_count_result.scalar_one()

        # AGREE and DISAGREE are verdict signals, not reactions.
        agree_count_result = await db.execute(
            select(func.count(PostVerdict.id)).where(
                PostVerdict.post_id == post.id,
                PostVerdict.verdict_type == VerdictType.AGREE,
            )
        )
        agree_count = agree_count_result.scalar_one()

        disagree_count_result = await db.execute(
            select(func.count(PostVerdict.id)).where(
                PostVerdict.post_id == post.id,
                PostVerdict.verdict_type == VerdictType.DISAGREE,
            )
        )
        disagree_count = disagree_count_result.scalar_one()

        # This count is only for explaining how much community validation
        # supported the v2 score. It is also used as a tie-breaker.
        community_validation_count = same_here_count + agree_count + disagree_count

        # Reuse the score service instead of copying the v2 formula here.
        buyer_regret_score = calculate_buyer_regret_score_v2(
            author_score=score.final_score,
            same_here_count=same_here_count,
            agree_count=agree_count,
            disagree_count=disagree_count,
        )

        ranking_items.append(
            BuyerRegretRankingItem(
                post_id=post.id,
                title=post.title,
                product_name=post.product_name,
                category=post.category,
                author_score=score.final_score,
                price_paid=post.price_paid,
                created_at=post.created_at,
                buyer_regret_score=buyer_regret_score,
                calculation_version=CALCULATION_VERSION_V2,
                same_here_count=same_here_count,
                agree_count=agree_count,
                disagree_count=disagree_count,
                community_validation_count=community_validation_count,
            )
        )

    # Rank by v2 score first. If scores tie, prefer the post with more
    # community validation. If that also ties, prefer the newer post.
    ranking_items.sort(
        key=lambda item: (
            item.buyer_regret_score,
            item.community_validation_count,
            item.created_at,
        ),
        reverse=True,
    )

    # Return only the requested top N ranking items.
    limited_items = ranking_items[:limit]

    return BuyerRegretRankingResponse(
        period=period,
        rankings=limited_items,
        count=len(limited_items),
    )


# Wallet Saved Ranking -----------------------------------------------------------
@router.get("/wallet-saved", response_model=WalletSavedRankingResponse)
async def get_wallet_saved_ranking(
    limit: int = Query(10, ge=1, le=100),
    db=Depends(get_db_session),
):
    query = (
        select(Post, func.count(PostReaction.id).label("saved_my_money_count"))
        .select_from(Post)
        .join(PostReaction, PostReaction.post_id == Post.id)
        .where(PostReaction.reaction_type == ReactionType.SAVED_MY_MONEY)
        .group_by(Post.id)
    )

    result = await db.execute(query)
    rows = result.all()

    ranking_items = []

    for post, saved_my_money_count in rows:
        estimated_money_saved = post.price_paid * saved_my_money_count

        ranking_items.append(
            WalletSavedRankingItem(
                post_id=post.id,
                title=post.title,
                product_name=post.product_name,
                category=post.category,
                price_paid=post.price_paid,
                currency=post.currency,
                created_at=post.created_at,
                estimated_money_saved=estimated_money_saved,
                saved_my_money_count=saved_my_money_count,
            )
        )

    ranking_items.sort(
        key=lambda item: (
            item.estimated_money_saved,
            item.saved_my_money_count,
            item.created_at,
        ),
        reverse=True,
    )
    limited_items = ranking_items[:limit]

    return WalletSavedRankingResponse(
        rankings=limited_items,
        count=len(limited_items),
    )
