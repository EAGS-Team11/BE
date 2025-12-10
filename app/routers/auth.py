# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_active_user, get_current_admin_user
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserOut, UserListOut, UserUpdate, StatusMessage, ResetRequest, PasswordReset 
from app.utils.auth import verify_password, create_access_token, hash_password 
from pydantic import BaseModel
import secrets # <-- Import secrets untuk token acak
from datetime import datetime, timedelta # <-- Import datetime

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

@router.put("/{nim_nip_target}", response_model=UserOut)
def update_user_by_admin(
    nim_nip_target: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user) # Memastikan hanya Admin
):
    user_to_update = db.query(User).filter(User.nim_nip == nim_nip_target).first()
    
    if not user_to_update:
        raise HTTPException(status_code=404, detail="User target not found")
        
    if user_data.nama is not None:
        user_to_update.nama = user_data.nama
    if user_data.prodi is not None:
        user_to_update.prodi = user_data.prodi
    if user_data.password is not None:
        user_to_update.password = hash_password(user_data.password)
        
    db.commit()
    db.refresh(user_to_update)
    return user_to_update

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



@router.post("/request-reset", status_code=status.HTTP_200_OK)
def request_password_reset(request: ResetRequest, db: Session = Depends(get_db)):
    """
    Membuat token reset dan menyimpannya di DB.
    (Simulasi: token dikembalikan di response, bukan dikirim via email).
    """
    user = db.query(User).filter(User.nim_nip == request.nim_nip).first()
    
    if not user:
        # Untuk keamanan, kita harus selalu merespons sukses
        # meskipun user tidak ditemukan (mencegah enumerasi user).
        return {"message": "If the NIM/NIP is registered, a password reset link has been sent."}

    # 1. Buat token acak (misal 32 byte = 64 karakter hex)
    token_reset = secrets.token_hex(32)
    expiry_time = datetime.utcnow() + timedelta(hours=1) # Token berlaku 1 jam

    # 2. Simpan token dan waktu kedaluwarsa di DB
    user.reset_token = token_reset
    user.reset_expires_at = expiry_time
    db.commit()
    
    # 3. Kirimkan token (SIMULASI: Mengembalikan token, bukan mengirim email)
    print(f"DEBUG: Token reset untuk {user.nim_nip}: {token_reset}")
    
    # Dalam produksi, response ini hanya berisi message sukses.
    # Kita tambahkan token untuk memudahkan testing frontend:
    return {
        "message": "Password reset token successfully generated.",
        "token": token_reset, # Hapus ini di produksi
        "nim_nip": user.nim_nip
    }


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(request: PasswordReset, db: Session = Depends(get_db)):
    """
    Mengatur password baru menggunakan token reset.
    """
    # 1. Cari user berdasarkan token dan pastikan token belum kedaluwarsa
    now = datetime.utcnow()
    user = db.query(User).filter(
        User.reset_token == request.token,
        User.reset_expires_at > now
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token."
        )

    # 2. Validasi password baru (opsional, tapi bagus untuk keamanan)
    if len(request.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters."
        )
        
    # 3. Hash password baru dan update DB
    user.password = hash_password(request.new_password)
    user.reset_token = None        # Hapus token setelah digunakan
    user.reset_expires_at = None   # Hapus waktu kedaluwarsa
    
    db.commit()

    return {"message": "Password successfully reset."}