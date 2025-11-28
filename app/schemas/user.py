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

class UserOut(BaseModel):
    id_user: int
    nim_nip: str
    nama: str
    role: RoleEnum
    prodi: str

    class Config:
        orm_mode = True