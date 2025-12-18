from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.sql import func

class Submission(Base):
    __tablename__ = "submissions"

    id_submission = Column(Integer, primary_key=True, index=True)
    id_assignment = Column(Integer, ForeignKey("assignments.id_assignment"), nullable=False)
    
    # --- TAMBAHKAN INI (Relasi ke Soal) ---
    id_question = Column(Integer, ForeignKey("questions.id_question"), nullable=False)
    
    id_mahasiswa = Column(Integer, ForeignKey("users.id_user"), nullable=False)
    
    # Jawaban spesifik untuk 1 soal itu
    jawaban = Column(Text, nullable=False)
    submitted_at = Column(TIMESTAMP, server_default=func.now())

    # Relasi
    assignment = relationship("Assignment", back_populates="submissions")
    mahasiswa = relationship("User", back_populates="submissions") 
    
    # Relasi ke Question
    question = relationship("Question", back_populates="submissions")

    # Relasi ke Grading (Nilai per soal)
    grading = relationship("Grading", back_populates="submission", uselist=False, cascade="all, delete-orphan")