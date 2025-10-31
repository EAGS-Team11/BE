from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
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
    role = Column(ENUM(RoleEnum), nullable=False)
    prodi = Column(String(100))
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
    updated_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP", onupdate="CURRENT_TIMESTAMP")

    courses = relationship("Course", back_populates="dosen")
    submissions = relationship("Submission", back_populates="mahasiswa")