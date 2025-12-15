# File: BE/app/schemas/grading.py

from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime

# Schema untuk input grading manual atau AI
class GradingCreate(BaseModel):
    id_submission: int
    skor_ai: Optional[Decimal] = None
    skor_dosen: Optional[Decimal] = None
    feedback_ai: Optional[str] = None
    feedback_dosen: Optional[str] = None

# Schema untuk output grading (dari database)
class GradingOut(BaseModel):
    id_grade: int
    id_submission: int
    skor_ai: Optional[Decimal]
    skor_dosen: Optional[Decimal]
    feedback_ai: Optional[str]
    feedback_dosen: Optional[str]
    graded_at: datetime

    class Config:
        # FastAPI/Pydantic v2
        from_attributes = True 

# Schema Input BARU untuk memicu Auto Grading AI
class AutoGradeRequest(BaseModel):
    id_submission: int = Field(..., description="ID Submission yang akan dinilai otomatis.")
    soal: str = Field(..., description="Teks Soal yang relevan.")
    kunci_jawaban: str = Field(..., description="Kunci jawaban atau panduan untuk penilaian.")
    max_score: float = Field(100.0, description="Skor maksimum untuk normalisasi hasil LLM.")