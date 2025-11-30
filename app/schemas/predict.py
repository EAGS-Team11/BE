# app/schemas/predict.py

from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
# from app.schemas.grading import GradingOut # Import ini jika diperlukan di sini

class PredictRequest(BaseModel):
    """Request untuk predict score essay (digunakan saat POST /predict/predict)"""
    id_submission: int
    keywords: Optional[list[str]] = None
    min_words: int = 100
    max_words: int = 5000
    
    class Config:
        # Pydantic V2 cleanup
        from_attributes = True 

class PredictResponse(BaseModel):
    """Response dari predict endpoint"""
    id_submission: int
    skor_ai: float
    feedback_ai: str
    level: str 
    
    class Config:
        from_attributes = True 

class UserStatsOut(BaseModel):
    """Schema untuk statistik dashboard Mahasiswa (digunakan saat GET /predict/my_stats)"""
    total_submitted: int = 0
    graded_count: int = 0
    pending_count: int = 0
    average_score: float = 0.0
    
    class Config:
        from_attributes = True