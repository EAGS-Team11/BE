# app/schemas/course.py
from pydantic import BaseModel

class CourseCreate(BaseModel):
    kode_course: str
    nama_course: str
    access_code: str

class CourseOut(BaseModel):
    id_course: int
    kode_course: str
    nama_course: str
    access_code: str

    class Config:
        from_attributes = True