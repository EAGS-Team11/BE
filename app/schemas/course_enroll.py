# app/schemas/course_enroll.py
from pydantic import BaseModel

class CourseEnrollCreate(BaseModel):
    id_course: int

class CourseEnrollOut(BaseModel):
    id_enroll: int
    id_course: int
    id_mahasiswa: int

    class Config:
        from_attributes = True