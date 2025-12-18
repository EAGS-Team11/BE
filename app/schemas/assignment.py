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
    bobot: int
    kunci_jawaban: Optional[str] = None

class QuestionOut(BaseModel):
    id_question: int
    nomor_soal: int
    teks_soal: str
    bobot: int
    kunci_jawaban: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# ==========================================
# 2. SCHEMA ASSIGNMENT
# ==========================================
class AssignmentCreate(BaseModel):
    id_course: int
    judul: str
    deskripsi: Optional[str] = None
    deadline: Optional[datetime] = None

class AssignmentWithQuestionsCreate(BaseModel):
    id_course: int
    judul: str
    deskripsi: Optional[str] = None
    deadline: Optional[datetime] = None
    questions: List[QuestionInput]

class AssignmentOut(BaseModel):
    id_assignment: int
    id_course: int
    judul: str
    deskripsi: Optional[str] = None
    deadline: Optional[datetime] = None
    created_at: Optional[datetime] = None

    # ✅ tampilkan total points assignment
    points: int = 0

    total_submitted: int = 0
    questions: List[QuestionOut] = []

    model_config = ConfigDict(from_attributes=True)
