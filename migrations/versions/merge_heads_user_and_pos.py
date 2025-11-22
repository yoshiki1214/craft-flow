"""Merge user and pos migrations

Revision ID: merge_heads
Revises: 541a5e112cfa, c243d5c775e7
Create Date: 2025-11-22 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "merge_heads"
down_revision = ("541a5e112cfa", "c243d5c775e7")
branch_labels = None
depends_on = None


def upgrade():
    # マージマイグレーションのため、実行する変更はありません
    pass


def downgrade():
    # マージマイグレーションのため、実行する変更はありません
    pass

