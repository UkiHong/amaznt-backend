from fastapi import APIRouter

# Health check endpoint, router for main.py
router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok"}
