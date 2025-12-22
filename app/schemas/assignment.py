# app/schemas/assignment.py

from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

# ==========================================
# 1. SCHEMA SOAL (QUESTION)
# ==========================================
class QuestionInput(BaseModel):
    id_question: Optional[int] = None
    nomor_soal: int
    teks_soal: str
    bobot: int = 10
    kunci_jawaban: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class QuestionOut(BaseModel):
    id_question: int
    nomor_soal: int
    teks_soal: str
    bobot: int
    kunci_jawaban: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Schema khusus Mahasiswa agar kunci jawaban tidak bocor
class QuestionStudentOut(BaseModel):
    id_question: int
    nomor_soal: int
    teks_soal: str
    bobot: int
    
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# 2. SCHEMA ASSIGNMENT
# ==========================================
class AssignmentCreate(BaseModel):
    id_course: int
    judul: str
    deskripsi: Optional[str] = None
    start_date: Optional[datetime] = None
    task_type: Optional[str] = "Essay"
    time_duration: Optional[str] = None
    # FIX: Ganti QuestionCreate menjadi QuestionInput
    questions: List[QuestionInput] 
    deadline: Optional[datetime] = None
    points: Optional[int] = 0 

    model_config = ConfigDict(from_attributes=True)

# Pastikan class ini ada jika router Anda memanggilnya
class AssignmentWithQuestionsCreate(AssignmentCreate):
    pass

class AssignmentOut(BaseModel):
    id_assignment: int
    id_course: int
    judul: str
    deskripsi: Optional[str] = None
    deadline: Optional[datetime] = None
    created_at: Optional[datetime] = None
    points: int = 0
    total_submitted: int = 0
    questions: List[QuestionOut] = []

    model_config = ConfigDict(from_attributes=True)

# Schema Output untuk Mahasiswa
class AssignmentStudentOut(BaseModel):
    id_assignment: int
    id_course: int
    judul: str
    deskripsi: Optional[str] = None
    deadline: Optional[datetime] = None
    points: int = 0
    questions: List[QuestionStudentOut] = []

    model_config = ConfigDict(from_attributes=True)