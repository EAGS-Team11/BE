# app/models/grading.py
from sqlalchemy import Column, Integer, DECIMAL, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base

class Grading(Base):
    __tablename__ = "grading"

    id_grade = Column(Integer, primary_key=True, index=True)
    id_submission = Column(Integer, ForeignKey("submissions.id_submission"), nullable=False)
    skor_ai = Column(DECIMAL(5,2))
    skor_dosen = Column(DECIMAL(5,2))
    feedback_ai = Column(Text)
    feedback_dosen = Column(Text)
    graded_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")

    submission = relationship("Submission", back_populates="grading")