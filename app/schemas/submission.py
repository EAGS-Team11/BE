# app/schemas/submission.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal
from app.schemas.user import UserOut # Import UserOut

# Schema untuk Assignment (Subset)
class AssignmentInfo(BaseModel):
    id_assignment: int
    judul: str
    deskripsi: Optional[str]
    deadline: Optional[datetime]
    
    class Config:
        from_attributes = True

# Schema untuk Grading (Subset)
class GradingInfo(BaseModel):
    skor_ai: Optional[Decimal]
    skor_dosen: Optional[Decimal]
    feedback_ai: Optional[str]
    graded_at: datetime
    
    class Config:
        from_attributes = True


class SubmissionDetailOut(BaseModel):
    """Schema Gabungan untuk menampilkan Submission + Grading + Assignment"""
    id_submission: int
    jawaban: str
    submitted_at: datetime
    
    # Relasi
    assignment: AssignmentInfo
    grading: Optional[GradingInfo] = None # Grading bisa saja belum ada
    mahasiswa: Optional[UserOut] = None # Detail mahasiswa
    
    class Config:
        from_attributes = True


class SubmissionOut(BaseModel):
    id_submission: int
    id_assignment: int
    id_mahasiswa: int
    jawaban: str
    submitted_at: datetime

    class Config:
        from_attributes = True

class SubmissionCreate(BaseModel):
    id_assignment: int
    jawaban: str