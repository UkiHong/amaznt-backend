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


# getting a single post
class PostResponse(BaseModel):
    # Enable ORM mode for SQLAlchemy models, needed for reading SQLAlchemy objects and attributes.
    # need this to convert SQLAlchemy object into pydantic model in api/posts.py
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


# getting a list of posts with count
class PostListResponse(BaseModel):
    posts: list[PostResponse]
    count: int
