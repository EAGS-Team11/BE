from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from decimal import Decimal
from datetime import datetime

from app.dependencies import get_db, get_current_active_user
from app.models.submissions import Submission
from app.models.grading import Grading
from app.models.user import User
from app.models.assignments import Assignment
from app.utils.ai_grader import grader
from app.schemas.predict import PredictResponse, UserStatsOut
from app.schemas.predict import PredictRequest, PredictResponse, GradingFullOut
from app.schemas.predict import GradingByDosen


router = APIRouter(tags=["predict"])

# ============================
# Helper level skor
# ============================
def _determine_level(score: float) -> str:
    if score >= 90:
        return "Excellent"
    elif score >= 75:
        return "Good"
    elif score >= 50:
        return "Fair"
    return "Needs Improvement"

# ============================
# 1. PREDICT SKOR (tidak disimpan)
# ============================
@router.post("/predict", response_model=PredictResponse)
def predict_score(
    id_submission: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(403, "Hanya dosen/admin yang dapat memprediksi skor.")

    submission = db.query(Submission).filter(
        Submission.id_submission == id_submission
    ).first()
    if not submission:
        raise HTTPException(404, "Submission tidak ditemukan.")

    assignment_data = db.query(Assignment).filter(
        Assignment.id_assignment == submission.id_assignment
    ).first()
    if not assignment_data:
        raise HTTPException(404, "Assignment tidak ditemukan.")

    max_score_dosen = assignment_data.points or 0

    hasil_ai = grader.grade_essay(
        soal=assignment_data.soal,
        kunci_jawaban=assignment_data.kunci_jawaban or "",
        jawaban_mahasiswa=submission.jawaban,
        max_score_dosen=max_score_dosen
    )

    final_score = hasil_ai["final_score"]
    level = _determine_level(final_score)

    return PredictResponse(
        id_submission=id_submission,
        skor_ai=final_score,
        feedback_ai=hasil_ai["feedback"],
        level=level
    )

# ============================
# 2. SIMPAN NILAI GRADING (AI + Dosen) ke DB
# ============================
@router.post("/grade", response_model=GradingFullOut)
def save_grade(
    request: GradingByDosen,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(403, "Hanya dosen/admin yang boleh menilai.")

    submission = db.query(Submission).filter(
        Submission.id_submission == request.id_submission
    ).first()
    if not submission:
        raise HTTPException(404, "Submission tidak ditemukan.")

    # Cek assignment
    assignment_data = db.query(Assignment).filter(
        Assignment.id_assignment == submission.id_assignment
    ).first()
    if not assignment_data:
        raise HTTPException(404, "Assignment tidak ditemukan.")

    # Ambil skor AI & feedback AI dari fungsi grader
    max_score_dosen = assignment_data.points or 0
    hasil_ai = grader.grade_essay(
        soal=assignment_data.soal,
        kunci_jawaban=assignment_data.kunci_jawaban or "",
        jawaban_mahasiswa=submission.jawaban,
        max_score_dosen=max_score_dosen
    )

    final_score_ai = Decimal(str(hasil_ai["final_score"]))
    feedback_ai = hasil_ai["feedback"]

    # Cek existing grading
    existing = db.query(Grading).filter(
        Grading.id_submission == request.id_submission
    ).first()

    if existing:
        existing.skor_dosen = request.skor_dosen
        existing.feedback_dosen = request.feedback_dosen
        existing.skor_ai = final_score_ai
        existing.feedback_ai = feedback_ai
        db.commit()
        db.refresh(existing)
        return existing

    new_grade = Grading(
        id_submission=request.id_submission,
        skor_dosen=request.skor_dosen,
        feedback_dosen=request.feedback_dosen,
        skor_ai=final_score_ai,
        feedback_ai=feedback_ai
    )

    db.add(new_grade)
    db.commit()
    db.refresh(new_grade)
    return new_grade


# ============================
# 3. GET GRADING BY SUBMISSION
# ============================
@router.get("/grade/{id_submission}", response_model=GradingFullOut)
def get_grade(
    id_submission: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    submission = db.query(Submission).filter(
        Submission.id_submission == id_submission
    ).first()
    if not submission:
        raise HTTPException(404, "Submission tidak ditemukan.")

    if current_user.role == "mahasiswa" and submission.id_mahasiswa != current_user.id_user:
        raise HTTPException(403, "Akses ditolak.")

    grading = db.query(Grading).filter(
        Grading.id_submission == id_submission
    ).first()
    if not grading:
        raise HTTPException(404, "Grading tidak ditemukan.")

    return grading

# ============================
# 4. STATISTIK MAHASISWA
# ============================
@router.get("/my_stats", response_model=UserStatsOut)
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "mahasiswa":
        raise HTTPException(403, "Akses ditolak.")

    total_sub = db.query(Submission).filter(
        Submission.id_mahasiswa == current_user.id_user
    ).count()

    graded_q = db.query(Submission).join(Grading).filter(
        Submission.id_mahasiswa == current_user.id_user
    )
    graded_count = graded_q.count()

    pending_count = db.query(Submission).outerjoin(Grading).filter(
        Submission.id_mahasiswa == current_user.id_user,
        Grading.id_submission.is_(None)
    ).count()

    avg_score_raw = graded_q.with_entities(sql_func.avg(Grading.skor_dosen)).scalar()
    avg_score = float(avg_score_raw) if avg_score_raw else 0.0

    return UserStatsOut(
        total_submitted=total_sub,
        graded_count=graded_count,
        pending_count=pending_count,
        average_score=round(avg_score, 1)
    )
