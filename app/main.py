import os

# to bring os.getenv()

from dotenv import load_dotenv

# to bring load_dotenv() function to load environment variables from a .env file

from fastapi import FastAPI
from app.schemas import PostCreateRequest, PostCreateResponse

load_dotenv()  # Load environment variables from .env file

app_name = os.getenv("APP_NAME")
debug_mode = os.getenv("DEBUG", "false").lower() == "true"


app = FastAPI(title="Amazn't Backend")


@app.get("/")
def read_root():
    return {
        "message": "Amazn't backend is running",
        "debug": debug_mode,
    }


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
