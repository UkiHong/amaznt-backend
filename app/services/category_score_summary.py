from decimal import Decimal

from sqlalchemy import func, select

from app.models.post import Post, ProductFailScore

MIN_CATEGORY_POST_COUNT = 5


async def get_category_score_summary(
    db,
    category: str,
    current_score: Decimal,
) -> dict:
    # Count posts in the same category and calculate their average regret score.
    # Post provides the category, ProductFailScore provides the final score.
    result = await db.execute(
        select(func.count(ProductFailScore.id), func.avg(ProductFailScore.final_score))
        .select_from(ProductFailScore)
        .join(Post, Post.id == ProductFailScore.post_id)
        .where(Post.category == category)
    )

    row = result.one()
    category_post_count = row[0]
    average_score = row[1]

    # Hide comparison values until the category has enough scored posts.
    if category_post_count < MIN_CATEGORY_POST_COUNT or average_score is None:
        return {
            "category_average_score": None,
            "score_delta": None,
            "category_post_count": category_post_count,
            "has_enough_data": False,
        }

    category_average_score = Decimal(str(average_score)).quantize(Decimal("0.01"))
    score_delta = (current_score - category_average_score).quantize(Decimal("0.01"))

    return {
        "category_average_score": category_average_score,
        "score_delta": score_delta,
        "category_post_count": category_post_count,
        "has_enough_data": True,
    }
