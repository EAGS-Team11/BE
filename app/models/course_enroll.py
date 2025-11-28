# app/models/course_enroll.py
from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.sql import func

class CourseEnroll(Base):
    __tablename__ = "course_enroll"

    id_enroll = Column(Integer, primary_key=True, index=True)
    id_course = Column(Integer, ForeignKey("course.id_course"), nullable=False)
    id_mahasiswa = Column(Integer, ForeignKey("users.id_user"), nullable=False)
    enroll_at = Column(TIMESTAMP, server_default=func.now())

    course = relationship("Course")
    mahasiswa = relationship("User")