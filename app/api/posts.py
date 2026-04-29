from sqlalchemy import select

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status

from app.core.security import get_current_active_user
from app.database import get_db_session
from app.models.post import Post, ProductFailScore
from app.services.product_fail_score_service import (
    CALCULATION_VERSION,
    calculate_final_score,
    get_grade,
    normalize_score,
)
from app.schemas.post import PostCreateRequest, PostListResponse, PostResponse

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    request: PostCreateRequest,
    db=Depends(get_db_session),
    current_user=Depends(get_current_active_user),
):
    # Creating a new post object to match the Post DB model.
    new_post = Post(
        author_id=current_user.id,
        title=request.title,
        product_name=request.product_name,
        price_paid=request.price_paid,
        fail_reason=request.fail_reason,
        platform=request.platform,
        product_url=request.product_url,
        category=request.category,
    )
    db.add(new_post)

    await db.flush()  # Flush to get the new_post.id for the ProductFailScore
    final_score = calculate_final_score(
        value_regret_score=request.value_regret_score,
        description_mismatch_score=request.description_mismatch_score,
        quality_disappointment_score=request.quality_disappointment_score,
        funniness_score=request.funniness_score,
        anger_score=request.anger_score,
    )

    # Creating a new ProductFailScore object to match the ProductFailScore DB model.
    new_score = ProductFailScore(
        post_id=new_post.id,
        value_regret_score=normalize_score(request.value_regret_score),
        description_mismatch_score=normalize_score(request.description_mismatch_score),
        quality_disappointment_score=normalize_score(
            request.quality_disappointment_score
        ),
        funniness_score=normalize_score(request.funniness_score),
        anger_score=normalize_score(request.anger_score),
        final_score=final_score,
        grade=get_grade(final_score),
        calculation_version=CALCULATION_VERSION,
    )
    db.add(new_score)

    await db.commit()
    await db.refresh(new_post)
    return new_post


@router.get("", response_model=PostListResponse)
async def get_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(5, ge=1, le=100),
    db=Depends(get_db_session),
):

    # offset is located under the get_posts because it's the server-side pagination logic, not from the user input.
    offset = (page - 1) * page_size

    result = await db.execute(
        select(Post).order_by(Post.created_at.desc()).offset(offset).limit(page_size)
    )
    posts = result.scalars().all()

    # This uses an N+1 query pattern for now. Optimize with a join or relationship loading later.
    post_responses = []
    for post in posts:
        score_result = await db.execute(
            select(ProductFailScore).where(ProductFailScore.post_id == post.id)
        )
        score = score_result.scalar_one_or_none()
        post_responses.append(
            {
                "id": post.id,
                "author_id": post.author_id,
                "title": post.title,
                "product_name": post.product_name,
                "price_paid": post.price_paid,
                "fail_reason": post.fail_reason,
                "platform": post.platform,
                "product_url": post.product_url or None,
                "category": post.category,
                "created_at": post.created_at,
                "score": score,
            }
        )

    return PostListResponse(
        posts=post_responses,
        count=len(post_responses),
        page=page,
        page_size=page_size,
    )


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    db=Depends(get_db_session),
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Getting the final score and grade from ProductFailScore table.
    score_result = await db.execute(
        select(ProductFailScore).where(ProductFailScore.post_id == post_id)
    )
    score = score_result.scalar_one_or_none()

    return {
        "id": post.id,
        "author_id": post.author_id,
        "title": post.title,
        "product_name": post.product_name,
        "price_paid": post.price_paid,
        "fail_reason": post.fail_reason,
        "platform": post.platform,
        "product_url": post.product_url or None,
        "category": post.category,
        "created_at": post.created_at,
        "score": score,
    }
