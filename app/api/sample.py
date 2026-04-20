from fastapi import APIRouter, HTTPException, status

from app.schemas import (
    PostCreateRequest,
    PostCreateResponse,
    PostResponse,
    PostListResponse,
)

# sample endpoint for router for main.py
router = APIRouter()


# sample posts for returning a list of PostListResponse
@router.get("/sample/posts", response_model=PostListResponse)
def get_sample_posts(limit: int = 10):
    sample_posts = [
        {"id": 1, "title": "sample title 1", "content": "sample content 1"},
        {"id": 2, "title": "sample title 2", "content": "sample content 2"},
        {"id": 3, "title": "sample title 3", "content": "sample content 3"},
        {"id": 4, "title": "sample title 4", "content": "sample content 4"},
        {"id": 5, "title": "sample title 5", "content": "sample content 5"},
    ]

    limited_posts = sample_posts[:limit]

    return PostListResponse(
        posts=limited_posts,
        count=len(limited_posts),
    )


# sample post creation for query parameter test with raising HTTPException for invalid input
@router.get("/sample/posts/{post_id}", response_model=PostResponse)
def get_sample_post(post_id: int):
    sample_posts = {
        1: {"id": 1, "title": "sample title 1", "content": "sample content 1"},
        2: {"id": 2, "title": "sample title 2", "content": "sample content 2"},
        3: {"id": 3, "title": "sample title 3", "content": "sample content 3"},
    }

    if post_id not in sample_posts:
        raise HTTPException(status_code=404, detail="Sample post not found")

    return sample_posts[post_id]


@router.post(
    "/sample/posts",
    response_model=PostCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sample_post(request: PostCreateRequest):
    return PostCreateResponse(
        id=1,
        title=request.title,
        content=request.content,
        message="sample post created",
    )
