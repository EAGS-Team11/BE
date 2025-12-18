# File: BE/app/schemas/submission.py

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from app.schemas.user import UserOut

# ============================================================
# 1. INPUT (CREATE SUBMISSION)
# ============================================================
class SubmissionItem(BaseModel):
    id_question: int
    jawaban: str

class SubmissionCreate(BaseModel):
    id_assignment: int
    items: List[SubmissionItem] 

class SubmissionResponse(BaseModel):
    message: str
    submitted_count: int

# ============================================================
# 2. OUTPUT DETAIL
# ============================================================

# --- PERBAIKAN PENTING DISINI ---
# Ubah semua field skor/feedback menjadi Optional agar tidak error 500
class GradingInfo(BaseModel):
    id_grade: Optional[int] = None
    
    # Field Nilai (Optional semua)
    grade: Optional[Decimal] = None
    feedback: Optional[str] = None
    technical_score: Optional[Decimal] = None
    llm_score: Optional[Decimal] = None
    
    skor_dosen: Optional[Decimal] = None
    feedback_dosen: Optional[str] = None
    
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
# --------------------------------

class AssignmentSimple(BaseModel):
    id_assignment: int
    judul: str
    model_config = ConfigDict(from_attributes=True)

class QuestionSimple(BaseModel):
    id_question: int
    nomor_soal: int
    teks_soal: str
    bobot: int
    model_config = ConfigDict(from_attributes=True)

class SubmissionDetailOut(BaseModel):
    id_submission: int
    id_assignment: int
    id_question: int
    id_mahasiswa: int
    jawaban: str
    submitted_at: datetime
    
    # Relasi
    mahasiswa: Optional[UserOut] = None
    grading: Optional[GradingInfo] = None # Ini bisa null jika belum dinilai
    question: Optional[QuestionSimple] = None
    assignment: Optional[AssignmentSimple] = None

    model_config = ConfigDict(from_attributes=True)