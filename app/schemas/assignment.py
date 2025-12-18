from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import List, Optional

# --- SCHEMA SOAL (QUESTION) ---
class QuestionBase(BaseModel):
    nomor_soal: int
    teks_soal: str
    kunci_jawaban: Optional[str] = None
    bobot: int = 10

class QuestionCreate(QuestionBase):
    pass

class QuestionResponse(QuestionBase):
    id_question: int
    class Config:
        from_attributes = True

# Schema Soal untuk Mahasiswa (Tanpa Kunci Jawaban)
class QuestionStudentOut(BaseModel):
    id_question: int
    nomor_soal: int
    teks_soal: str
    bobot: int
    # kunci_jawaban di-hide
    class Config:
        from_attributes = True

# --- INPUT (CREATE) ---
class AssignmentCreate(BaseModel):
    id_course: int
    judul: str
    deskripsi: Optional[str] = None
    start_date: Optional[datetime] = None
    task_type: Optional[str] = "Essay"
    time_duration: Optional[str] = None
    questions: List[QuestionCreate] 
    deadline: Optional[datetime] = None
    points: Optional[int] = 0 

# --- OUTPUT (READ) ---
class AssignmentStudentOut(BaseModel):
    id_assignment: int
    id_course: int
    judul: str
    deskripsi: Optional[str]
    start_date: Optional[datetime]
    task_type: Optional[str]
    time_duration: Optional[str]
    
    # Field questions WAJIB ada dan berupa List
    questions: List[QuestionStudentOut] = [] 
    
    points: Optional[int]
    deadline: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class AssignmentTeacherOut(BaseModel):
    id_assignment: int
    id_course: int
    judul: str
    deskripsi: Optional[str]
    start_date: Optional[datetime]
    task_type: Optional[str]
    time_duration: Optional[str]
    questions: List[QuestionResponse] = []
    points: Optional[int]
    deadline: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True