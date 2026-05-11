from enum import Enum

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


# This one is a Python Enum
class ReactionType(str, Enum):
    """Domain reaction for a post.

    Policy v1:
    - One user can have only one reaction per post.
    - Same reaction again means toggle off.
    - Different reaction replaces the previous one.
    - Post authors cannot react to their own posts.
    """

    # Useful review signal. Used for Confidence Score v1.
    # ex) "This review was useful while deciding whether to buy."
    HELPFUL = "HELPFUL"

    # Same bad purchase experience signal. Used for Confidence Score v1.
    # ex) "I bought this too, and the same thing happened to me."
    SAME_HERE = "SAME_HERE"

    # The review helped avoid buying the product. Used for Impact Score v1.
    # ex) "This review helped me avoid buying this product."
    SAVED_MY_MONEY = "SAVED_MY_MONEY"


class PostReaction(Base):
    __tablename__ = "post_reactions"

    # one user can have one reaction per post.
    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uq_post_reactions_user_post"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )
    post_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("posts.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    reaction_type: Mapped[ReactionType] = mapped_column(
        SQLEnum(ReactionType, name="reaction_type"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
