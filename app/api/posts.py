from pathlib import Path
from uuid import uuid4

from sqlalchemy import func, select

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from starlette import status

from app.core.security import get_current_active_user
from app.database import get_db_session
from app.models.post import Comment, Post, PostImage, ProductFailScore
from app.services.product_fail_score_service import (
    CALCULATION_VERSION,
    calculate_final_score,
    get_grade,
    normalize_score,
)
from app.schemas.post import (
    CommentCreateRequest,
    CommentListResponse,
    CommentResponse,
    PostCreateRequest,
    PostImageResponse,
    PostListResponse,
    PostResponse,
    PostUpdateRequest,
)

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)


MAX_IMAGES_PER_POST = 5
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MEDIA_ROOT = Path("media")
POST_IMAGE_DIR = MEDIA_ROOT / "post-images"


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
    return {
        "id": new_post.id,
        "author_id": new_post.author_id,
        "title": new_post.title,
        "product_name": new_post.product_name,
        "price_paid": new_post.price_paid,
        "fail_reason": new_post.fail_reason,
        "platform": new_post.platform,
        "product_url": new_post.product_url or None,
        "category": new_post.category,
        "created_at": new_post.created_at,
        "score": new_score,
    }


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

    images_result = await db.execute(
        select(PostImage).where(PostImage.post_id == post_id)
    )
    images = images_result.scalars().all()

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
        "images": images,
    }


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    request: PostUpdateRequest,
    db=Depends(get_db_session),
    current_user=Depends(get_current_active_user),
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post",
        )

    score_result = await db.execute(
        select(ProductFailScore).where(ProductFailScore.post_id == post_id)
    )
    score = score_result.scalar_one_or_none()
    if score is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Score not found",
        )

    post_fields = {
        "title",
        "product_name",
        "price_paid",
        "fail_reason",
        "platform",
        "product_url",
        "category",
    }

    score_fields = {
        "value_regret_score",
        "description_mismatch_score",
        "quality_disappointment_score",
        "funniness_score",
        "anger_score",
    }

    # Update only the fields that are provided in the request (partial update).
    update_data = request.model_dump(exclude_unset=True)

    # Check if any score fields are updated. If yes, final_score will be recalculated.
    score_changed = any(key in score_fields for key in update_data)

    for key, value in update_data.items():
        if key in post_fields:
            if value is None and key != "product_url":
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"{key} cannot be null",
                )
            setattr(post, key, value)

        elif key in score_fields:
            if value is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"{key} cannot be null",
                )
            setattr(score, key, normalize_score(value))

    # "// 20" is to convert the normalized score back to the original 1-5 scale for final score calculation.
    if score_changed:
        score.final_score = calculate_final_score(
            value_regret_score=score.value_regret_score // 20,
            description_mismatch_score=score.description_mismatch_score // 20,
            quality_disappointment_score=score.quality_disappointment_score // 20,
            funniness_score=score.funniness_score // 20,
            anger_score=score.anger_score // 20,
        )
        score.grade = get_grade(score.final_score)

    await db.commit()
    await db.refresh(post)

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


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    db=Depends(get_db_session),
    current_user=Depends(get_current_active_user),
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post",
        )

    # Deleting the associated score first, which is related to Post model with a foreign key.
    # could be refactored with cascade delete later?
    score_result = await db.execute(
        select(ProductFailScore).where(ProductFailScore.post_id == post_id)
    )
    score = score_result.scalar_one_or_none()
    if score:
        await db.delete(score)

    await db.delete(post)
    await db.commit()


# Comments Routers--------------------------------------------------------------------
@router.post(
    "/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    post_id: int,
    request: CommentCreateRequest,
    db=Depends(get_db_session),
    current_user=Depends(get_current_active_user),
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    new_comment = Comment(
        post_id=post_id,
        author_id=current_user.id,
        content=request.content,
    )

    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment


# GET all comments for {post_id} post
@router.get("/{post_id}/comments", response_model=CommentListResponse)
async def get_comments(
    post_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db=Depends(get_db_session),
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    offset = (page - 1) * page_size

    comments_result = await db.execute(
        select(Comment)
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    comments = comments_result.scalars().all()

    return CommentListResponse(
        comments=comments,
        count=len(comments),
        page=page,
        page_size=page_size,
    )


# Posting images / Limit a post can have up to 5 images, but the API itself only allow upload one file at once.
# Need update for uploading 5 file at the same time.
@router.post(
    "/{post_id}/images",
    response_model=PostImageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_post_image(
    post_id: int,
    file: UploadFile = File(
        ...
    ),  # request from a user when uploading files, "..." means file is mandatory.
    db=Depends(get_db_session),
    current_user=Depends(get_current_active_user),
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload images for this post",
        )

    image_count_result = await db.execute(
        select(func.count(PostImage.id)).where(PostImage.post_id == post_id)
    )
    image_count = image_count_result.scalar_one()
    # Limit image upload counts up to 5.
    if image_count >= MAX_IMAGES_PER_POST:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A post can have up to 5 images.",
        )

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is required."
        )

    file_extension = Path(
        file.filename
    ).suffix.lower()  # lower() is for accepting uppercase extensions ex) JPG.

    if file_extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only jpg/jpeg/png/webp images are allowed.",
        )

    if file.content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image/jpeg, image/png, and image/webp are allowed.",
        )

    file_bytes = await file.read()
    file_size = len(file_bytes)

    if file_size > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image size must be 5MB or less.",
        )

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Image file is empty."
        )

    # uuid4() is to make a unique file names.
    stored_filename = f"{uuid4()}{file_extension}"

    # file is stored in local DB for now to avoid DB getting heavy.
    # it's also easy to move them to S3 storage later.
    post_image_dir = POST_IMAGE_DIR / str(post_id)
    post_image_dir.mkdir(parents=True, exist_ok=True)

    stored_file_path = post_image_dir / stored_filename
    stored_file_path.write_bytes(file_bytes)

    new_image = PostImage(
        post_id=post_id,
        original_filename=file.filename,
        stored_filename=stored_filename,
        file_path=str(stored_file_path),
        content_type=file.content_type,
        file_size=file_size,
    )

    db.add(new_image)
    await db.commit()
    await db.refresh(new_image)
    return new_image


@router.get("/{post_id}/images", response_model=list[PostImageResponse])
async def get_post_images(
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

    images_result = await db.execute(
        select(PostImage)
        .where(PostImage.post_id == post_id)
        .order_by(PostImage.created_at.desc())
    )
    images = images_result.scalars().all()
    return images


@router.delete(
    "/{post_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_comment(
    post_id: int,
    comment_id: int,
    db=Depends(get_db_session),
    current_user=Depends(get_current_active_user),
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    comment_result = await db.execute(
        select(Comment).where(
            Comment.id == comment_id,
            Comment.post_id == post_id,
        )
    )
    comment = comment_result.scalar_one_or_none()

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed for deletion",
        )

    await db.delete(comment)
    await db.commit()
