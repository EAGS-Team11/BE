"""add reset token columns

Revision ID: bc034a6fc013
Revises: 9187565ee637
Create Date: 2025-12-15 03:41:30.170192

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bc034a6fc013'
down_revision: Union[str, Sequence[str], None] = '9187565ee637'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Menambahkan kolom reset_token dan reset_expires_at ke tabel users
    op.add_column('users', sa.Column('reset_token', sa.String(), nullable=True))
    op.add_column('users', sa.Column('reset_expires_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Menghapus kolom jika migrasi dibatalkan (rollback)
    op.drop_column('users', 'reset_expires_at')
    op.drop_column('users', 'reset_token')