from fastapi import FastAPI
from app.schemas import PostCreateRequest, PostCreateResponse

app = FastAPI(title="Amazn't Backend")


@app.get("/")
def read_root():
    return {"message": "Amazn't backend is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/sample/posts", response_model=PostCreateResponse)
def create_sample_post(request: PostCreateRequest):
    return PostCreateResponse(
        id=1,
        title=request.title,
        content=request.content,
        message="sample post created",
    )
