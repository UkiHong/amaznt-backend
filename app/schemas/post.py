# Schemas for POST-related API requests and responses
from pydantic import BaseModel


class PostCreateRequest(BaseModel):
    title: str
    content: str


class PostCreateResponse(BaseModel):
    id: int
    title: str
    content: str
    message: str


# getting a single post
class PostResponse(BaseModel):
    id: int
    title: str
    content: str


# getting a list of posts with count
class PostListResponse(BaseModel):
    posts: list[PostResponse]
    count: int
