from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

# ============================================================
# Request untuk AI prediction (tanpa disimpan)
# ============================================================
class PredictRequest(BaseModel):
    """
    Body untuk POST /predict/predict
    """
    id_submission: int   # submission yang mau dinilai

    model_config = ConfigDict(from_attributes=True)

# ============================================================
# Response untuk AI grading sementara (predict)
# ============================================================
class PredictResponse(BaseModel):
    """
    Response untuk hasil grading AI (tanpa disimpan)
    """
    id_submission: int
    skor_ai: Decimal          # nilai 0–100 hasil AI
    feedback_ai: str          # penjelasan AI
    level: str                # Excellent, Good, Poor, dll

    model_config = ConfigDict(from_attributes=True)


# Request grading dari dosen
class GradingByDosen(BaseModel):
    id_submission: int
    skor_dosen: Decimal
    feedback_dosen: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

# Response grading lengkap (AI + Dosen)
class GradingFullOut(BaseModel):
    id_grade: int
    id_submission: int
    skor_ai: Optional[Decimal] = None
    skor_dosen: Optional[Decimal] = None
    feedback_ai: Optional[str] = None
    feedback_dosen: Optional[str] = None
    graded_at: datetime
    model_config = ConfigDict(from_attributes=True)
# ============================================================
# Statistik mahasiswa
# ============================================================
class UserStatsOut(BaseModel):
    total_submitted: int = 0
    graded_count: int = 0
    pending_count: int = 0
    average_score: float = 0.0

    model_config = ConfigDict(from_attributes=True)
