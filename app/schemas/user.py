# app/schemas/user.py
from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import Optional

class RoleEnum(str, Enum):
    admin = "admin"
    dosen = "dosen"
    mahasiswa = "mahasiswa"

class UserCreate(BaseModel):
    nim_nip: str
    password: str
    nama: str
    role: RoleEnum
    prodi: str

class UserLogin(BaseModel):
    nim_nip: str
    password: str

class UserOut(BaseModel):
    id_user: int
    nim_nip: str
    nama: str
    role: RoleEnum
    prodi: str

    class Config:
        from_attributes = True

class UserListOut(BaseModel):
    """Schema untuk admin melihat daftar semua user (tanpa password)."""
    id_user: int
    nim_nip: str
    nama: str
    role: RoleEnum
    prodi: str
    # --- PERBAIKAN: GANTI str menjadi datetime ---
    created_at: datetime 
    updated_at: datetime 

    class Config:
        from_attributes = True # (Asumsi Anda sudah menggunakan V2)

# --- PERUBAHAN BARU 1: Schema untuk Update/Edit Profil ---
class UserUpdate(BaseModel):
    # NIM/NIP, Role, dan ID tidak boleh diubah melalui endpoint ini
    nama: Optional[str] = None
    password: Optional[str] = None
    prodi: Optional[str] = None
    
    class Config:
        from_attributes = True

# --- PERUBAHAN BARU 2: Schema untuk Response Deaktivasi ---
class StatusMessage(BaseModel):
    message: str

class ResetRequest(BaseModel):
    """Skema untuk meminta token reset"""
    nim_nip: str

class PasswordReset(BaseModel):
    """Skema untuk mengatur password baru menggunakan token"""
    token: str
    new_password: str