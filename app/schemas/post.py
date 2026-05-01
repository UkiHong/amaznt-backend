# Schemas for POST-related API requests and responses
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PostCreateRequest(BaseModel):
    title: str
    product_name: str
    price_paid: Decimal
    fail_reason: str
    platform: str
    product_url: str | None = None
    category: str
    value_regret_score: int = Field(
        ge=1, le=5, description="Score for value regret, between 1 and 5"
    )
    description_mismatch_score: int = Field(
        ge=1, le=5, description="Score for description mismatch, between 1 and 5"
    )
    quality_disappointment_score: int = Field(
        ge=1, le=5, description="Score for quality disappointment, between 1 and 5"
    )
    funniness_score: int = Field(
        ge=1, le=5, description="Score for funniness, between 1 and 5"
    )
    anger_score: int = Field(ge=1, le=5, description="Score for anger, between 1 and 5")


class ProductFailScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    final_score: Decimal
    grade: str
    calculation_version: str


# getting a single post
class PostResponse(BaseModel):
    # Allows Pydantic to build this response model from a SQLAlchemy ORM object.
    # Without this, Pydantic expects a dict-like object and may fail when we return a Post model instance.
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: int
    title: str
    product_name: str
    price_paid: Decimal
    fail_reason: str
    platform: str
    product_url: str | None = None
    category: str
    created_at: datetime

    score: ProductFailScoreResponse | None = None


# getting a list of posts with count
class PostListResponse(BaseModel):
    posts: list[PostResponse]
    count: int
    page: int
    page_size: int


class PostUpdateRequest(BaseModel):
    title: str | None = None
    product_name: str | None = None
    price_paid: Decimal | None = None
    fail_reason: str | None = None
    platform: str | None = None
    product_url: str | None = None
    category: str | None = None

    value_regret_score: int | None = Field(
        default=None, ge=1, le=5, description="Score for value regret, between 1 and 5"
    )
    description_mismatch_score: int | None = Field(
        default=None,
        ge=1,
        le=5,
        description="Score for description mismatch, between 1 and 5",
    )
    quality_disappointment_score: int | None = Field(
        default=None,
        ge=1,
        le=5,
        description="Score for quality disappointment, between 1 and 5",
    )
    funniness_score: int | None = Field(
        default=None, ge=1, le=5, description="Score for funniness, between 1 and 5"
    )
    anger_score: int | None = Field(
        default=None, ge=1, le=5, description="Score for anger, between 1 and 5"
    )


# Comments Schemas--------------------------------------------------------------------
class CommentCreateRequest(BaseModel):
    content: str = Field(min_length=3, max_length=500)


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    post_id: int
    author_id: int
    content: str
    created_at: datetime


class CommentListResponse(BaseModel):
    comments: list[CommentResponse]
    count: int
