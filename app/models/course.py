# app/models/course.py
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base

class Course(Base):
    __tablename__ = "course"

    id_course = Column(Integer, primary_key=True, index=True)
    kode_course = Column(String(50), unique=True, nullable=False)
    nama_course = Column(String(100), nullable=False)
    id_dosen = Column(Integer, ForeignKey("users.id_user"), nullable=False)
    access_code = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
    updated_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP", onupdate="CURRENT_TIMESTAMP")

    dosen = relationship("User", back_populates="courses")
    assignments = relationship("Assignment", back_populates="course")