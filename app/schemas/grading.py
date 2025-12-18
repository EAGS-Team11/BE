# app/schemas/grading.py

from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from decimal import Decimal
from datetime import datetime


class GradingCreate(BaseModel):
    id_submission: int
    skor_ai: Optional[float] = None
    skor_dosen: Optional[float] = None
    feedback_ai: Optional[str] = None
    feedback_dosen: Optional[str] = None


class GradingOut(BaseModel):
    id_grade: int
    id_submission: int
    skor_ai: Optional[float] = None
    skor_dosen: Optional[float] = None
    feedback_ai: Optional[str] = None
    feedback_dosen: Optional[str] = None
    graded_at: Optional[datetime] = None

    # ✅ Pydantic v2
    model_config = ConfigDict(from_attributes=True)

    # ✅ kalau DB ngasih Decimal, convert ke float biar FE aman
    @field_validator("skor_ai", "skor_dosen", mode="before")
    @classmethod
    def _decimal_to_float(cls, v):
        if v is None:
            return None
        if isinstance(v, Decimal):
            return float(v)
        return v
