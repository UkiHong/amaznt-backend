# Schemas for POST-related API requests and responses
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PostCreateRequest(BaseModel):
    title: str
    product_name: str
    price_paid: Decimal
    fail_reason: str
    platform: str
    product_url: str | None = None
    category: str


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
