# File: BE/app/routers/grading.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal
import logging  # <--- Tambahan Wajib

from app.dependencies import get_db, get_current_active_user
from app.models.grading import Grading
from app.models.submissions import Submission 
from app.models.user import User
from app.schemas.grading import GradingCreate, GradingOut, AutoGradeRequest

# Import instance LLM Grader (Pastikan file app/utils/ai_grader.py ada)
from app.utils.ai_grader import grader as llm_grader 

router = APIRouter(tags=["grading"])

# ===========================
# 1. Endpoint: Auto Grading oleh AI
# ===========================
@router.post("/auto", response_model=GradingOut, status_code=status.HTTP_201_CREATED)
def auto_grade_submission(
    request_data: AutoGradeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(status_code=403, detail="Hanya dosen/admin yang boleh memicu penilaian AI.")

    submission = db.query(Submission).filter(
        Submission.id_submission == request_data.id_submission
    ).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission tidak ditemukan.")
    
    if not submission.jawaban:
         raise HTTPException(status_code=400, detail="Submission tidak memiliki jawaban.")

    try:
        llm_result = llm_grader.grade_essay(
            soal=request_data.soal,
            kunci_jawaban=request_data.kunci_jawaban,
            jawaban_mahasiswa=submission.jawaban,
            max_score_dosen=request_data.max_score
        )
    except Exception as e:
        logging.error(f"Error LLM: {e}")
        raise HTTPException(status_code=500, detail=f"Gagal memanggil LLM Grader: {e}")

    if llm_result.get("method") == "Error":
         raise HTTPException(status_code=503, detail=f"AI Error: {llm_result.get('feedback')}")
    
    skor_ai_decimal = Decimal(str(llm_result["final_score"]))
    feedback_ai_text = llm_result["feedback"]

    existing_grade = db.query(Grading).filter(
        Grading.id_submission == request_data.id_submission
    ).first()

    if existing_grade:
        existing_grade.skor_ai = skor_ai_decimal
        existing_grade.feedback_ai = feedback_ai_text
        db_obj = existing_grade
    else:
        new_grade = Grading(
            id_submission=request_data.id_submission,
            skor_ai=skor_ai_decimal,
            feedback_ai=feedback_ai_text,
            skor_dosen=None, feedback_dosen=None,
            technical_score=Decimal(str(llm_result.get("technical_score", 0))),
            llm_score=Decimal(str(llm_result.get("llm_score", 0)))
        )
        db.add(new_grade)
        db_obj = new_grade

    db.commit()
    db.refresh(db_obj)
    return db_obj


# ===========================
# 2. Endpoint: Manual Grading Dosen
# ===========================
# PERBAIKAN: Path harus "/grade_submission" agar sesuai Frontend
@router.post("/grade_submission", response_model=GradingOut, status_code=status.HTTP_201_CREATED)
def grade_submission(
    grade_data: GradingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(status_code=403, detail="Hanya dosen/admin yang boleh menilai.")

    submission = db.query(Submission).filter(
        Submission.id_submission == grade_data.id_submission
    ).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission tidak ditemukan.")

    existing_grade = db.query(Grading).filter(
        Grading.id_submission == grade_data.id_submission
    ).first()

    if existing_grade:
        # Update nilai dosen
        if grade_data.skor_dosen is not None:
            existing_grade.skor_dosen = Decimal(str(grade_data.skor_dosen))
        if grade_data.feedback_dosen is not None:
            existing_grade.feedback_dosen = grade_data.feedback_dosen
        
        db_obj = existing_grade
    else:
        # Buat baru
        new_grade = Grading(
            id_submission=grade_data.id_submission,
            skor_dosen=Decimal(str(grade_data.skor_dosen)) if grade_data.skor_dosen is not None else None,
            feedback_dosen=grade_data.feedback_dosen,
            skor_ai=0, feedback_ai="Belum dinilai AI",
            technical_score=0, llm_score=0
        )
        db.add(new_grade)
        db_obj = new_grade

    db.commit()
    db.refresh(db_obj)
    return db_obj

# ===========================
# 3. Endpoint: Get Grading
# ===========================
@router.get("/{id_submission}", response_model=GradingOut)
def get_grading(
    id_submission: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    grading = db.query(Grading).filter(Grading.id_submission == id_submission).first()
    if not grading:
        raise HTTPException(status_code=404, detail="Grading tidak ditemukan.")
    
    return grading