from typing import Sequence, Union # <-- FIX: Memastikan Union dan Sequence diimpor

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.~
revision: str = 'b680bc9ecd95'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Mengubah nama kolom 'soal' menjadi 'question' untuk sinkronisasi dengan model Python."""
    
    # Tindakan ini dilakukan karena log database menunjukkan kolom 'soal' ada, 
    # tetapi aplikasi FastAPI Anda mencari kolom 'question'.
    # Kami menggunakan existing_type=sa.Text() karena kolom 'soal' sudah berjenis TEXT.
    op.alter_column('assignments', 'soal', new_column_name='question', existing_type=sa.Text())
    
    # Catatan: Kolom 'kunci_jawaban' sudah ada di skema database yang Anda kirimkan, 
    # sehingga operasi penambahan (op.add_column) yang ada di skrip sebelumnya dihapus 
    # untuk menghindari error 'column already exists'.


def downgrade() -> None:
    """Downgrade schema: Mengembalikan nama kolom 'question' menjadi 'soal'."""
    
    # Mengembalikan nama kolom 'question' menjadi 'soal'
    op.alter_column('assignments', 'question', new_column_name='soal', existing_type=sa.Text())