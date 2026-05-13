from app.models.reaction import ReactionType
from pydantic import BaseModel


class ReactionToggleResponse(BaseModel):
    status: str
    post_id: int
    reaction_type: ReactionType | None = None


class ReactionSummaryResponse(BaseModel):
    helpful_count: int = 0
    same_here_count: int = 0
    saved_my_money_count: int = 0
