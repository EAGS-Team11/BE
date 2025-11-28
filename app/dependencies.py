# app/dependencies.py

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.user import User # Impor model apapun
from sqlalchemy.engine import URL, create_engine
import os
from sqlalchemy import text

# Fungsi Dependency untuk FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fungsi untuk membuat database secara programatis jika belum ada
# Catatan: Fungsi ini hanya perlu dipanggil di awal (main.py)
def create_database_if_not_exists():
    db_name = os.getenv("DB_NAME")
    
    # 1. Buat URL dasar yang terhubung ke DB default (postgres)
    base_url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database="postgres" # Hubungkan ke database default
    )
    
    # 2. Coba buat koneksi ke database default
    try:
        base_engine = create_engine(base_url, isolation_level="AUTOCOMMIT") # Pindah isolation_level ke sini
        with base_engine.connect() as connection:
            
            # CEK DATABASE (Gunakan text() untuk SQL mentah)
            check_query = text(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'")
            result = connection.execute(check_query)
            
            if not result.scalar():
                print(f"Creating database {db_name}...")
                
                # BUAT DATABASE (Gunakan text() untuk SQL mentah)
                create_db_query = text(f"CREATE DATABASE {db_name} ENCODING 'utf8' TEMPLATE template0")
                connection.execute(create_db_query)
                
            print(f"Database '{db_name}' is ready.")
            
    except Exception as e:
        # Masih gagal koneksi. Fatal error.
        print(f"FATAL DATABASE ERROR: {e}")
        print("Please check if your Docker container is running or if your credentials are correct.")