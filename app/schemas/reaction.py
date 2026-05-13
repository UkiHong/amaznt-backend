from app.models.reaction import ReactionType
from pydantic import BaseModel


class ReactionToggleResponse(BaseModel):
    status: str
    post_id: int
    reaction_type: ReactionType | None = None
