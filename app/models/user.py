# app/models/user.py
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.sql import func
from enum import Enum
from app.database import Base


class RoleEnum(str, Enum):
    admin = "admin"
    dosen = "dosen"
    mahasiswa = "mahasiswa"

class User(Base):
    __tablename__ = "users"

    id_user = Column(Integer, primary_key=True, index=True)
    nama = Column(String(100), nullable=False)
    nim_nip = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(ENUM(RoleEnum, name="role_enum"), nullable=False)
    prodi = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now()) # Perhatikan onupdate juga diubah
    
    courses = relationship("Course", back_populates="dosen")
    submissions = relationship("Submission", back_populates="mahasiswa")