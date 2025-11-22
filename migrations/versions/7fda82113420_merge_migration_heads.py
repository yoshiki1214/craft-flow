"""Merge migration heads

Revision ID: 7fda82113420
Revises: 596dda9b64c1, 5fc011630d7c
Create Date: 2025-11-22 15:59:41.331460

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7fda82113420'
down_revision = ('596dda9b64c1', '5fc011630d7c')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
