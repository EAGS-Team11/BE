# app/models/assignments.py

from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Assignment(Base):
    __tablename__ = "assignments"

    id_assignment = Column(Integer, primary_key=True, index=True)

    # tabel Course kamu bernama "course"
    id_course = Column(Integer, ForeignKey("course.id_course"), nullable=False)

    judul = Column(String(200), nullable=False)
    deskripsi = Column(Text, nullable=True)
    deadline = Column(DateTime, nullable=True)

    # ✅ WAJIB: sesuai error DB kamu
    # kalau di DB sudah NOT NULL, ini harus ada di model juga
    points = Column(Integer, nullable=False, server_default="0")

    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id_user"), nullable=True)

    # Relasi
    course = relationship("Course", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment")

    questions = relationship(
        "Question",
        back_populates="assignment",
        cascade="all, delete-orphan"
    )
