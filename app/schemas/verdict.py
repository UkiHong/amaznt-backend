from pydantic import BaseModel

from app.models.verdict import VerdictType


class VerdictToggleResponse(BaseModel):
    status: str
    post_id: int
    verdict_type: VerdictType | None = None


class VerdictSummaryResponse(BaseModel):
    agree_count: int = 0
    disagree_count: int = 0
