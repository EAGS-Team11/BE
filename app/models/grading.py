# app/models/grading.py

from sqlalchemy import Column, Integer, DECIMAL, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.sql import func

class Grading(Base):
    __tablename__ = "grading"

    id_grade = Column(Integer, primary_key=True, index=True)
    id_submission = Column(Integer, ForeignKey("submissions.id_submission"), nullable=False)
    
    # Kolom Nilai Utama
    skor_ai = Column(DECIMAL(5,2), nullable=True)
    skor_dosen = Column(DECIMAL(5,2), nullable=True)
    
    # Kolom Feedback
    feedback_ai = Column(Text, nullable=True)
    feedback_dosen = Column(Text, nullable=True)
    
    # --- KOLOM BARU (WAJIB DITAMBAHKAN) ---
    # Ini untuk menampung detail nilai dari AI
    technical_score = Column(DECIMAL(5,2), default=0)
    llm_score = Column(DECIMAL(5,2), default=0)
    # ---------------------------------------

    # Timestamp (tambah onupdate agar waktu berubah saat diedit)
    graded_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    submission = relationship("Submission", back_populates="grading")