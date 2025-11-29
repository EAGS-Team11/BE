# app/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.engine import URL, create_engine
from sqlalchemy import text # Wajib untuk create_database_if_not_exists
from jose import JWTError, jwt
from app.database import SessionLocal, engine
from app.models.user import User
from app.config import settings
from pydantic import BaseModel
import os


# Schemas untuk token
class TokenData(BaseModel):
    nim_nip: str | None = None

# Skema otentikasi HTTP Bearer (menyederhanakan OpenAPI sehingga Swagger tidak menampilkan
# form OAuth2 yang meminta client_id/client_secret)
# Gunakan scheme_name="bearerAuth" agar cocok dengan nama di custom_openapi() → hanya satu Authorize
http_bearer = HTTPBearer(scheme_name="bearerAuth")

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

# Fungsi Dependency untuk memverifikasi token dan mendapatkan user
def get_current_user(db: Session = Depends(get_db), token: HTTPAuthorizationCredentials = Depends(http_bearer)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 1. Decode Payload JWT (ambil token dari credentials)
        raw_token = token.credentials if hasattr(token, "credentials") else token
        payload = jwt.decode(raw_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        nim_nip: str = payload.get("sub") # 'sub' adalah field untuk subject (nim_nip)
        if nim_nip is None:
            raise credentials_exception
        token_data = TokenData(nim_nip=nim_nip)
    except JWTError:
        raise credentials_exception
    
    # 2. Ambil User dari Database
    user = db.query(User).filter(User.nim_nip == token_data.nim_nip).first()
    if user is None:
        raise credentials_exception
    return user # Mengembalikan objek User SQLAlchemy

# Fungsi Dependency yang akan digunakan di router (misalnya untuk Course atau Assignment)
def get_current_active_user(current_user: User = Depends(get_current_user)):
    # Saat ini, semua user yang login dianggap aktif
    return current_user

# Fungsi Dependency untuk memverifikasi bahwa user adalah admin
def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can access this resource"
        )
    return current_user