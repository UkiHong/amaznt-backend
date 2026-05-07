"""add cascade delete to post children

Revision ID: 0786d0324929
Revises: f77400cb214e
Create Date: 2026-05-07 22:30:46.379353

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0786d0324929"
down_revision: Union[str, Sequence[str], None] = "f77400cb214e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        "product_fail_scores_post_id_fkey",
        "product_fail_scores",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "product_fail_scores_post_id_fkey",
        "product_fail_scores",
        "posts",
        ["post_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(
        "comments_post_id_fkey",
        "comments",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "comments_post_id_fkey",
        "comments",
        "posts",
        ["post_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(
        "post_images_post_id_fkey",
        "post_images",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "post_images_post_id_fkey",
        "post_images",
        "posts",
        ["post_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "product_fail_scores_post_id_fkey",
        "product_fail_scores",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "product_fail_scores_post_id_fkey",
        "product_fail_scores",
        "posts",
        ["post_id"],
        ["id"],
    )

    op.drop_constraint(
        "comments_post_id_fkey",
        "comments",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "comments_post_id_fkey",
        "comments",
        "posts",
        ["post_id"],
        ["id"],
    )

    op.drop_constraint(
        "post_images_post_id_fkey",
        "post_images",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "post_images_post_id_fkey",
        "post_images",
        "posts",
        ["post_id"],
        ["id"],
    )
