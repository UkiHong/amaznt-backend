from fastapi import APIRouter


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.get("/auth-check")
def health_check():
    return {"status": "ok"}
