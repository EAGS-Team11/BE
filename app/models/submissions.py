# app/models/submissions.py

from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.sql import func


class Submission(Base):
    __tablename__ = "submissions"

    id_submission = Column(Integer, primary_key=True, index=True)
    id_assignment = Column(Integer, ForeignKey("assignments.id_assignment"), nullable=False)
    id_mahasiswa = Column(Integer, ForeignKey("users.id_user"), nullable=False)
    jawaban = Column(Text, nullable=False)
    submitted_at = Column(TIMESTAMP, server_default=func.now())

    # Gunakan string 'Assignment' dan 'User'
    assignment = relationship("Assignment", back_populates="submissions")
    mahasiswa = relationship("User", back_populates="submissions") 
    
    # Gunakan string 'Grading'
    grading = relationship("Grading", back_populates="submission", uselist=False)