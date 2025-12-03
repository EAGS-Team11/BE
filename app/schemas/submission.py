from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from decimal import Decimal
from app.schemas.user import UserOut


# ============================================================
#  Assignment Info (subset untuk tampil di Submission)
# ============================================================
class AssignmentInfo(BaseModel):
    id_assignment: int
    id_course: int
    judul: str
    soal: str              # <-- FIX: pakai "question" sesuai model Assignment
    deskripsi: Optional[str]
    points: int
    deadline: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


# ============================================================
#  Grading Info (subset untuk tampil di Submission)
# ============================================================
class GradingInfo(BaseModel):
    grade: Optional[Decimal]              # skor akhir AI
    technical_score: Optional[Decimal]    # skor semantic similarity
    llm_score: Optional[Decimal]          # skor reasoning LLM
    feedback: Optional[str]               # feedback AI
    created_at: datetime                  # pastikan model Grading pakai field ini

    model_config = ConfigDict(from_attributes=True)


# ============================================================
#  Submission Detail Output (gabungan)
# ============================================================
class SubmissionDetailOut(BaseModel):
    id_submission: int
    jawaban: str
    submitted_at: datetime

    # Relasi
    assignment: AssignmentInfo
    grading: Optional[GradingInfo] = None
    mahasiswa: Optional[UserOut] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================
#  Submission Output Simple
# ============================================================
class SubmissionOut(BaseModel):
    id_submission: int
    id_assignment: int
    id_mahasiswa: int
    jawaban: str
    submitted_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
#  Submission Create (input)
# ============================================================
class SubmissionCreate(BaseModel):
    id_assignment: int
    jawaban: str
