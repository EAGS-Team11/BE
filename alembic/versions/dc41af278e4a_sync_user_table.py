# File: alembic/versions/dc41af278e4a_...py

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
# Menggunakan DateTime(timezone=True) memerlukan import datetime jika tidak ada di SQL Alchemy
from sqlalchemy.dialects import postgresql 

# =========================================================
# VARIABEL GLOBAL (HARUS ADA UNTUK ALEMBIK)
# =========================================================
# ID Revisi Saat Ini (Harus sesuai dengan nama file)
revision: str = 'dc41af278e4a'

# ID Revisi Sebelumnya (Ganti dengan ID migrasi sebelumnya Anda)
# Anda menyebut '9187565ee637' sebelumnya, kita gunakan itu.
down_revision: Union[str, Sequence[str], None] = '9187565ee637' 

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
# =========================================================


def upgrade() -> None:
    """Upgrade schema: Menambahkan reset_token dan reset_expires_at."""
    
    # 1. Tambahkan kolom reset_token
    op.add_column(
        "users",
        sa.Column("reset_token", sa.String(length=100), nullable=True) 
    )
    
    # 2. Tambahkan kolom reset_expires_at
    op.add_column(
        "users",
        # Menggunakan DateTime dengan timezone seperti yang diminta oleh model Anda
        sa.Column("reset_expires_at", sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema: Menghapus reset_token dan reset_expires_at."""
    
    # 1. Hapus kolom reset_expires_at
    op.drop_column("users", "reset_expires_at")
    
    # 2. Hapus kolom reset_token
    op.drop_column("users", "reset_token")