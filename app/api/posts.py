from sqlalchemy import select

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.core.security import get_current_active_user
from app.database import get_db_session
from app.models.post import Post
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
    await db.commit()
    await db.refresh(new_post)
    return new_post


@router.get("", response_model=PostListResponse)
async def get_posts(
    db=Depends(get_db_session),
):
    result = await db.execute(select(Post))
    posts = result.scalars().all()
    return PostListResponse(
        posts=posts,
        count=len(posts),
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
    return post
