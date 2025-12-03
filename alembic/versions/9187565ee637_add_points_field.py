"""add points field

Revision ID: 9187565ee637
Revises: b680bc9ecd95
Create Date: 2025-12-03 01:45:01.819980
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '9187565ee637'
down_revision: Union[str, Sequence[str], None] = 'b680bc9ecd95'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add points column to assignments."""
    op.add_column(
        'assignments',
        sa.Column('points', sa.Integer(), nullable=True)
    )


def downgrade() -> None:
    """Remove points column."""
    op.drop_column('assignments', 'points')
