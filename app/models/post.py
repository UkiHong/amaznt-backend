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
    fail_reason: Mapped[str] = mapped_column(String(300), nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    product_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
