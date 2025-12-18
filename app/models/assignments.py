from sqlalchemy import Column, Integer, String, ForeignKey, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.sql import func

class Assignment(Base):
    __tablename__ = "assignments"

    id_assignment = Column(Integer, primary_key=True, index=True)
    id_course = Column(Integer, ForeignKey("course.id_course"), nullable=False)

    judul = Column(String(200), nullable=False)
    deskripsi = Column(Text, nullable=True)
    
    # --- KOLOM BARU ---
    start_date = Column(TIMESTAMP, nullable=True)     # Kapan tugas mulai dibuka
    task_type = Column(String(50), default="Essay")   # Essay, Quiz, Project
    time_duration = Column(String(100), nullable=True) # "2 Jam 30 Menit" (Sesuai input FE)
    # ------------------

    points = Column(Integer, nullable=False, default=100)
    deadline = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relasi
    course = relationship("Course", back_populates="assignments")
    questions = relationship("Question", back_populates="assignment", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="assignment")