from pydantic import BaseModel


class PostCreateRequest(BaseModel):
    title: str
    content: str


class PostCreateResponse(BaseModel):
    id: int
    title: str
    content: str
    message: str
