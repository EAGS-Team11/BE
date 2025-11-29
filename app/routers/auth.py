# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status # Tambah status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserOut # Tambah UserOut
from app.utils.auth import verify_password, create_access_token, hash_password # Tambah hash_password
from pydantic import BaseModel

router = APIRouter(tags=["auth"])

# Skema Response Login Baru
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut # Menyertakan detail user

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Cek apakah NIP/NIM sudah terdaftar
    db_user = db.query(User).filter(User.nim_nip == user.nim_nip).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="NIM/NIP sudah terdaftar"
        )
    
    # Hash password sebelum menyimpan
    hashed_password = hash_password(user.password)
    
    # Buat instance User baru
    new_user = User(
        nim_nip=user.nim_nip,
        password=hashed_password,
        nama=user.nama,
        role=user.role,
        prodi=user.prodi
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Endpoint login
@router.post("/login", response_model=Token) # <-- Ganti response_model menjadi Token
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.nim_nip == user.nim_nip).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # Payload token hanya berisi sub (nim_nip)
    token = create_access_token({"sub": db_user.nim_nip})
    
    # Kembalikan token dan objek user lengkap (menggunakan UserOut schema)
    return {
        "access_token": token, 
        "token_type": "bearer",
        "user": db_user # SQLAlchemy model akan otomatis diubah ke UserOut
    }