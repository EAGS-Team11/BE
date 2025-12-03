from pydantic import BaseModel
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

# Schema untuk output grading
class GradingOut(BaseModel):
    id_grade: int
    id_submission: int
    skor_ai: Optional[Decimal]
    skor_dosen: Optional[Decimal]
    feedback_ai: Optional[str]
    feedback_dosen: Optional[str]
    graded_at: datetime

    class Config:
        from_attributes = True
