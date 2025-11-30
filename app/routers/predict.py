# app/routers/predict.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from decimal import Decimal
from pydantic import BaseModel
from typing import Optional

from app.dependencies import get_db, get_current_active_user
from app.models.submissions import Submission
from app.models.grading import Grading
from app.models.user import User
from app.utils.scoring import calculate_essay_score, get_feedback_level
from app.schemas.grading import GradingOut
from app.schemas.predict import PredictResponse, PredictRequest, UserStatsOut # Import UserStatsOut

router = APIRouter(tags=["predict"])


# ===== Schemas =====
class PredictRequest(BaseModel):
    """Request untuk predict score essay"""
    id_submission: int
    keywords: Optional[list[str]] = None  # Optional keyword untuk matching
    min_words: int = 100
    max_words: int = 5000


class PredictResponse(BaseModel):
    """Response dari predict endpoint"""
    id_submission: int
    skor_ai: float
    feedback_ai: str
    level: str  # Excellent, Good, Fair, Needs Improvement


# ===== Endpoints =====

@router.post("/predict", response_model=PredictResponse)
def predict_score(
    request: PredictRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Predict score untuk submission berdasarkan essay content.
    Hanya dosen/admin yang bisa access endpoint ini.
    """
    # Verifikasi role
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya dosen atau admin yang dapat melakukan prediksi skor."
        )
    
    # Cari submission
    submission = db.query(Submission).filter(
        Submission.id_submission == request.id_submission
    ).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Submission dengan ID {request.id_submission} tidak ditemukan."
        )
    
    # Calculate score
    score, feedback = calculate_essay_score(
        essay_text=submission.jawaban,
        keywords=request.keywords,
        min_words=request.min_words,
        max_words=request.max_words
    )
    
    level = get_feedback_level(score)
    
    return PredictResponse(
        id_submission=request.id_submission,
        skor_ai=score,
        feedback_ai=feedback,
        level=level
    )


@router.post("/grade", response_model=GradingOut)
def save_grade(
    request: PredictRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Predict score dan SIMPAN ke database sebagai Grading.
    Hanya dosen/admin yang bisa access endpoint ini.
    """
    # Verifikasi role
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya dosen atau admin yang dapat menyimpan grading."
        )
    
    # Cari submission
    submission = db.query(Submission).filter(
        Submission.id_submission == request.id_submission
    ).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Submission dengan ID {request.id_submission} tidak ditemukan."
        )
    
    # Check if grading already exists
    existing_grading = db.query(Grading).filter(
        Grading.id_submission == request.id_submission
    ).first()
    
    # Calculate score
    score, feedback = calculate_essay_score(
        essay_text=submission.jawaban,
        keywords=request.keywords,
        min_words=request.min_words,
        max_words=request.max_words
    )
    
    if existing_grading:
        # Update existing grading
        existing_grading.skor_ai = Decimal(str(score))
        existing_grading.feedback_ai = feedback
        db.commit()
        db.refresh(existing_grading)
        return existing_grading
    else:
        # Create new grading
        new_grading = Grading(
            id_submission=request.id_submission,
            skor_ai=Decimal(str(score)),
            feedback_ai=feedback
        )
        db.add(new_grading)
        db.commit()
        db.refresh(new_grading)
        return new_grading


@router.get("/grade/{id_submission}", response_model=GradingOut)
def get_grade(
    id_submission: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Dapatkan grading untuk submission tertentu.
    """
    grading = db.query(Grading).filter(
        Grading.id_submission == id_submission
    ).first()
    
    if not grading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grading untuk submission {id_submission} tidak ditemukan."
        )
    
    return grading



@router.get("/my_stats", response_model=UserStatsOut)
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "mahasiswa":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akses ditolak.")

    # 1. Total Submissions
    total_submitted = db.query(Submission).filter(
        Submission.id_mahasiswa == current_user.id_user
    ).count()

    # 2. Submissions yang sudah dinilai
    # Join Submission dengan Grading
    graded_submissions = db.query(Submission).join(Grading).filter(
        Submission.id_mahasiswa == current_user.id_user
    )
    graded_count = graded_submissions.count()

    # 3. Submissions yang belum dinilai
    # Left Join Submission dengan Grading, dan cek mana yang grading.id_grade IS NULL
    pending_submissions = db.query(Submission).outerjoin(Grading).filter(
        Submission.id_mahasiswa == current_user.id_user,
        Grading.id_grade.is_(None)
    )
    pending_count = pending_submissions.count()
    
    # 4. Hitung Average Score (hanya dari yang sudah dinilai)
    avg_score_decimal = graded_submissions.with_entities(
        sql_func.avg(Grading.skor_ai)
    ).scalar()
    
    avg_score = float(avg_score_decimal) if avg_score_decimal else 0.0

    return UserStatsOut(
        total_submitted=total_submitted,
        graded_count=graded_count,
        pending_count=pending_count,
        average_score=round(avg_score, 1)
    )