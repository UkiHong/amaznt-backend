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
class VerdictType(str, Enum):
    """Domain verdict for a post.

    Policy v1:
    - One user can have only one verdict per post.
    - Same verdict again means toggle off.
    - Different verdict replaces the previous one.
    - Post authors cannot leave verdicts on their own posts.
    """

    AGREE = "AGREE"
    DISAGREE = "DISAGREE"


class PostVerdict(Base):
    __tablename__ = "post_verdicts"

    # one user can have one verdict per post.
    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uq_post_verdicts_user_post"),
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
    verdict_type: Mapped[VerdictType] = mapped_column(
        SQLEnum(VerdictType, name="verdict_type"),
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
