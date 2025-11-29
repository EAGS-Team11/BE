from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.sql import func
from app.models.grading import Grading # Pastikan diimpor jika ada

class Submission(Base):
    __tablename__ = "submissions"

    id_submission = Column(Integer, primary_key=True, index=True)
    id_assignment = Column(Integer, ForeignKey("assignments.id_assignment"), nullable=False)
    id_mahasiswa = Column(Integer, ForeignKey("users.id_user"), nullable=False)
    jawaban = Column(Text, nullable=False)
    submitted_at = Column(TIMESTAMP, server_default=func.now())

    assignment = relationship("Assignment", back_populates="submissions")
    
    # --- PERBAIKAN RELASI BALIK ---
    mahasiswa = relationship("User", back_populates="submissions") 
    
    # Tambahkan relasi ke Grading, karena Grading memiliki ForeignKey ke Submission
    grading = relationship("Grading", back_populates="submission", uselist=False) # uselist=False karena 1 submission hanya punya 1 grade