# app/models/assignments.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base

class Assignment(Base):
    __tablename__ = "assignments"

    id_assignment = Column(Integer, primary_key=True, index=True)
    id_course = Column(Integer, ForeignKey("course.id_course"), nullable=False)
    judul = Column(String(200), nullable=False)
    deskripsi = Column(Text)
    deadline = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")

    course = relationship("Course", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment")