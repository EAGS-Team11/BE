from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b680bc9ecd95'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # KITA UBAH DISINI:
    # Daripada rename kolom 'soal' (yang tidak ada), kita langsung buat kolom 'question' baru.
    op.add_column('assignments', sa.Column('question', sa.Text(), nullable=True))


def downgrade() -> None:
    # Jika migrasi dibatalkan, hapus kolom 'question'
    op.drop_column('assignments', 'question')