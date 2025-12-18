# app/models/questions.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Question(Base):
    __tablename__ = "questions"

    id_question = Column(Integer, primary_key=True, index=True)
    
    # Kunci: Soal ini milik Assignment yang mana?
    id_assignment = Column(Integer, ForeignKey("assignments.id_assignment", ondelete="CASCADE"), nullable=False)
    
    nomor_soal = Column(Integer, nullable=False)
    teks_soal = Column(Text, nullable=False)
    bobot = Column(Integer, nullable=False)
    kunci_jawaban = Column(Text, nullable=True)

    # Relasi Balik
    assignment = relationship("Assignment", back_populates="questions")
    submissions = relationship("Submission", back_populates="question", cascade="all, delete-orphan")