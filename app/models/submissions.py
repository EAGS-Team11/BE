# app/models/submissions.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Submission(Base):
    __tablename__ = "submissions"

    id_submission = Column(Integer, primary_key=True, index=True)
    id_assignment = Column(Integer, ForeignKey("assignments.id_assignment"), nullable=False)
    id_mahasiswa = Column(Integer, ForeignKey("users.id_user"), nullable=False)
    
    # --- PENTING: Link ke Soal (Question) ---
    id_question = Column(Integer, ForeignKey("questions.id_question"), nullable=False)
    # ----------------------------------------
    
    jawaban = Column(Text, nullable=False)
    submitted_at = Column(DateTime, server_default=func.now())

    # Relasi
    assignment = relationship("Assignment", back_populates="submissions")
    mahasiswa = relationship("User", back_populates="submissions")
    grading = relationship("Grading", uselist=False, back_populates="submission")
    
    # Relasi ke Question (Agar backend tahu ini jawaban untuk soal apa)
    question = relationship("Question", back_populates="submissions")