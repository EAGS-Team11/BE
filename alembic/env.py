import sys
import os
from logging.config import fileConfig
from typing import NoReturn

from sqlalchemy import engine_from_config, pool
from alembic import context

# --- KONFIGURASI PATH PROJECT ---
# Tentukan direktori dasar (BE) dan tambahkan ke sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# --- IMPORT BASE METADATA ---
try:
    # Asumsikan Base dan metadata didefinisikan di app.database atau diimpor di sana
    from app.database import Base
    target_metadata = Base.metadata
except ImportError:
    # Tangani kasus di mana app.database tidak ditemukan atau Base tidak ada
    print("FATAL: Gagal mengimpor Base dari app.database. Pastikan path project sudah benar dan model telah didefinisikan.")
    # Exit dengan kode error agar Alembic tidak mencoba menjalankan migrasi tanpa metadata
    sys.exit(1)
except Exception as e:
    # Tangani error lain saat loading model (misalnya, error sintaks di model)
    print(f"FATAL: Error saat memuat model SQLAlchemy: {e}")
    sys.exit(1)


# --- KONFIGURASI INI ALEMBIK ---
config = context.config

# Logging config dari alembic.ini
if config.config_file_name:
    # Menggunakan try-except karena fileConfig bisa gagal jika file log tidak ditemukan/format salah
    try:
        fileConfig(config.config_file_name)
    except Exception as e:
        # Peringatan, tapi tidak menghentikan migrasi (karena logging opsional)
        print(f"WARNING: Gagal mengkonfigurasi logging: {e}")


def run_migrations_offline() -> None:
    """Jalankan migrasi dalam mode 'offline'.
    Ini hanya menghasilkan SQL, tidak terhubung ke database.
    """
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Sertakan parameter compare_... di mode offline juga untuk konsistensi
        compare_type=True,
        compare_server_default=True,
        compare_nullable=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Jalankan migrasi dalam mode 'online'.
    Terhubung ke database dan menjalankan DDL/DML secara langsung.
    """
    try:
        connectable = engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
    except Exception as e:
        print(f"FATAL: Gagal membuat engine database dari konfigurasi: {e}")
        # Hentikan proses jika gagal terhubung ke database
        sys.exit(1)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Deteksi perubahan tipe kolom
            compare_server_default=True,  # Deteksi perubahan default value
            compare_nullable=True,  # Deteksi perubahan nullable
            # Tambahkan juga schema compare jika Anda menggunakan schema non-default PostgreSQL
            # compare_to_dependencies=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# --- EKSEKUSI UTAMA ---
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()