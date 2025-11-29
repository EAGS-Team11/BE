# app/schemas/user.py
from pydantic import BaseModel
from enum import Enum

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
        orm_mode = True

class UserListOut(BaseModel):
    """Schema untuk admin melihat daftar semua user (tanpa password)."""
    id_user: int
    nim_nip: str
    nama: str
    role: RoleEnum
    prodi: str
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True