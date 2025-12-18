# File: BE/app/schemas/grading.py

from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime

# --- INPUT: Saat Dosen memberi nilai manual ---
# KITA NAMAKAN 'GradingCreate' AGAR MATCH DENGAN ROUTER
class GradingCreate(BaseModel):
    id_submission: int
    skor_dosen: float
    feedback_dosen: Optional[str] = None

# --- OUTPUT: Format data keluar dari Database ---
class GradingOut(BaseModel):
    id_grade: int
    id_submission: int
    skor_ai: Optional[Decimal]
    skor_dosen: Optional[Decimal]
    feedback_ai: Optional[str]
    feedback_dosen: Optional[str]
    graded_at: Optional[datetime]

    class Config:
        from_attributes = True 

# --- INPUT: Untuk Auto Grading AI ---
class AutoGradeRequest(BaseModel):
    id_submission: int
    soal: str
    kunci_jawaban: str
    max_score: float = 100.0