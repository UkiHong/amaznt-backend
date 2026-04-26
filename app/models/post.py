from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func

from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column


class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    product_name: Mapped[str] = mapped_column(String(100), nullable=False)
    price_paid: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, server_default="GBP"
    )
    fail_reason: Mapped[str] = mapped_column(String(300), nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    product_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
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


class ProductFailScore(Base):
    __tablename__ = "product_fail_scores"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("posts.id"), unique=True, nullable=False
    )

    value_regret_score: Mapped[int] = mapped_column(Integer, nullable=False)
    description_mismatch_score: Mapped[int] = mapped_column(Integer, nullable=False)
    quality_disappointment_score: Mapped[int] = mapped_column(Integer, nullable=False)
    funniness_score: Mapped[int] = mapped_column(Integer, nullable=False)
    anger_score: Mapped[int] = mapped_column(Integer, nullable=False)
    final_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    grade: Mapped[str] = mapped_column(String(50), nullable=False)

    calculation_version: Mapped[str] = mapped_column(String(50), nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
