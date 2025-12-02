# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_active_user, get_current_admin_user
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserOut, UserListOut, UserUpdate, StatusMessage 
from app.utils.auth import verify_password, create_access_token, hash_password 
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


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    """Return currently authenticated user (requires Bearer token)."""
    return current_user


@router.get("/users", response_model=list[UserListOut])
def list_all_users(admin_user: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    """
    Admin endpoint: list semua user dalam sistem.
    Hanya admin yang dapat mengakses endpoint ini.
    Response tidak termasuk plain password (hanya data publik).
    """
    users = db.query(User).all()
    return users

# --- ENDPOINT BARU 1: EDIT PROFIL (/auth/me) ---
@router.put("/me", response_model=UserOut)
def update_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Cek dan update field yang disediakan
    
    if user_data.nama is not None:
        current_user.nama = user_data.nama
    
    if user_data.prodi is not None:
        current_user.prodi = user_data.prodi
        
    if user_data.password is not None:
        # Hashing password baru sebelum menyimpan
        hashed_password = hash_password(user_data.password)
        current_user.password = hashed_password

    db.commit()
    db.refresh(current_user)
    return current_user


# --- ENDPOINT BARU 2: HAPUS AKUN (/auth/delete_me) ---
# CATATAN: Karena model User tidak memiliki kolom 'is_active', kita akan
# Hapus User secara permanen (Hard Delete) atau tambahkan kolom 'is_active'
# Untuk keamanan data, kita ubah role menjadi 'deactivated' (asumsi kita tambahkan)
# Namun, karena role adalah Enum, kita lakukan Hard Delete atau tambahkan field baru.
# Kita asumsikan Hard Delete (Hati-hati, ini bisa menyebabkan data relasi terputus)
# Untuk menghindari error relasi (Foreign Key Constraint), kita akan HAPUS PERMANEN
# HANYA JIKA TIDAK ADA RELASI, atau Lakukan Soft Delete (disarankan).

# Kita tambahkan kolom status/active di model User. Untuk sementara, kita pakai Hard Delete sederhana.

@router.delete("/delete_me", response_model=StatusMessage)
def delete_my_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Cek apakah user memiliki relasi data (Course, Submission, Enrollment)
    # Jika tidak ada, kita Hard Delete. Jika ada, kita tolak atau lakukan Soft Delete.
    
    # Check for related data (contoh: Submission)
    if db.query(User).filter(User.id_user == current_user.id_user).join(User.submissions).count() > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Akun tidak dapat dihapus karena sudah memiliki data submission yang terhubung. Hubungi Admin untuk deaktivasi manual."
        )

    # Lakukan Hard Delete (hapus permanen)
    db.delete(current_user)
    db.commit()
    
    return StatusMessage(message=f"Akun dengan NIM/NIP {current_user.nim_nip} berhasil dihapus permanen.")
