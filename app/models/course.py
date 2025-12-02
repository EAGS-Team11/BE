# app/models/course.py

from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.sql import func
# HAPUS: from app.models.course_enroll import CourseEnroll 
from app.models.user import User # Import User

class Course(Base):
    __tablename__ = "course"

    id_course = Column(Integer, primary_key=True, index=True)
    kode_course = Column(String(50), unique=True, nullable=False)
    nama_course = Column(String(100), nullable=False)
    id_dosen = Column(Integer, ForeignKey("users.id_user"), nullable=False)
    access_code = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    dosen = relationship("User", back_populates="courses")
    # --- PENTING: TAMBAHKAN cascade="all, delete-orphan" ---
    assignments = relationship("Assignment", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("CourseEnroll", back_populates="course", cascade="all, delete-orphan")

