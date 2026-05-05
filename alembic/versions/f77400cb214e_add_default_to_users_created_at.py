"""add default to users created_at

Revision ID: f77400cb214e
Revises: cd9304deb66c
Create Date: 2026-05-05 02:22:48.131770

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f77400cb214e"
down_revision: Union[str, Sequence[str], None] = "cd9304deb66c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=None,
        existing_nullable=False,
    )
