# app/models/assignments.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.sql import func

class Assignment(Base):
    __tablename__ = "assignments"

    id_assignment = Column(Integer, primary_key=True, index=True)

    # Relasi ke course
    id_course = Column(Integer, ForeignKey("course.id_course"), nullable=False)

    # Field utama
    judul = Column(String(200), nullable=False)
    deskripsi = Column(Text, nullable=True)
    soal = Column(Text, nullable=True)
    kunci_jawaban = Column(Text, nullable=True)

    # Points wajib
    points = Column(Integer, nullable=False, default=100)

    deadline = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    course = relationship("Course", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment")
