# File: BE/app/routers/grading.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal

# Import dependencies yang ada
from app.dependencies import get_db, get_current_active_user
from app.models.grading import Grading
# ASUMSI: Submission model ada di app/models/submissions
from app.models.submissions import Submission 
from app.models.user import User
from app.schemas.grading import GradingCreate, GradingOut, AutoGradeRequest

# Import instance LLM Grader
from app.utils.ai_grader import grader as llm_grader 

router = APIRouter(tags=["grading"])

# ===========================
# Endpoint BARU: Auto Grading oleh AI
# ===========================
@router.post("/auto", response_model=GradingOut, status_code=status.HTTP_201_CREATED, summary="Menilai submission otomatis menggunakan LLM (Groq)")
def auto_grade_submission(
    request_data: AutoGradeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 1. Autentikasi dan Otorisasi
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(status_code=403, detail="Hanya dosen/admin yang boleh memicu penilaian AI.")

    # 2. Ambil Submission
    submission = db.query(Submission).filter(
        Submission.id_submission == request_data.id_submission
    ).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission tidak ditemukan.")
    
    # Validasi bahwa submission memiliki konten jawaban
    # ASUMSI: Kolom jawaban mahasiswa di model Submission adalah 'jawaban'
    if not submission.jawaban:
         raise HTTPException(status_code=400, detail="Submission tidak memiliki jawaban yang dapat dinilai.")

    # 3. Panggil LLM Grader
    try:
        llm_result = llm_grader.grade_essay(
            soal=request_data.soal,
            kunci_jawaban=request_data.kunci_jawaban,
            jawaban_mahasiswa=submission.jawaban, # Gunakan konten jawaban dari DB
            max_score_dosen=request_data.max_score
        )
    except Exception as e:
        logging.error(f"Error saat memanggil LLM: {e}")
        raise HTTPException(status_code=500, detail=f"Gagal memanggil LLM Grader: {e}")

    # 4. Tangani Kegagalan LLM (API Key, Koneksi)
    if llm_result["method"] == "Error":
         raise HTTPException(
            status_code=503,
            detail=f"Layanan Grading AI tidak tersedia: {llm_result['feedback']}"
        )
    
    # Konversi float hasil LLM ke Decimal untuk database
    skor_ai_decimal = Decimal(str(llm_result["final_score"]))
    feedback_ai_text = llm_result["feedback"]

    # 5. Simpan/Update Hasil AI ke Database
    existing_grade = db.query(Grading).filter(
        Grading.id_submission == request_data.id_submission
    ).first()

    if existing_grade:
        # Update grading yang sudah ada (hanya kolom AI)
        existing_grade.skor_ai = skor_ai_decimal
        existing_grade.feedback_ai = feedback_ai_text
        
        db.commit()
        db.refresh(existing_grade)
        return existing_grade
    else:
        # Buat grading baru dengan hasil AI
        new_grade = Grading(
            id_submission=request_data.id_submission,
            skor_ai=skor_ai_decimal,
            feedback_ai=feedback_ai_text
        )
        db.add(new_grade)
        db.commit()
        db.refresh(new_grade)
        return new_grade

# ===========================
# Manual grading oleh dosen/admin (TETAP SAMA)
# ===========================
@router.post("/", response_model=GradingOut, status_code=status.HTTP_201_CREATED)
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
        # Update grading yang sudah ada
        if grade_data.skor_dosen is not None:
            existing_grade.skor_dosen = Decimal(str(grade_data.skor_dosen))
        if grade_data.feedback_dosen is not None:
            existing_grade.feedback_dosen = grade_data.feedback_dosen
        # Memastikan kolom AI tetap utuh jika tidak diisi oleh dosen
        if grade_data.skor_ai is not None:
            existing_grade.skor_ai = Decimal(str(grade_data.skor_ai))
        if grade_data.feedback_ai is not None:
            existing_grade.feedback_ai = grade_data.feedback_ai

        db.commit()
        db.refresh(existing_grade)
        return existing_grade
    else:
        # Buat grading baru
        new_grade = Grading(
            id_submission=grade_data.id_submission,
            skor_dosen=Decimal(str(grade_data.skor_dosen)) if grade_data.skor_dosen is not None else None,
            feedback_dosen=grade_data.feedback_dosen,
            skor_ai=Decimal(str(grade_data.skor_ai)) if grade_data.skor_ai is not None else None,
            feedback_ai=grade_data.feedback_ai
        )
        db.add(new_grade)
        db.commit()
        db.refresh(new_grade)
        return new_grade

# ===========================
# Ambil grading by submission (TETAP SAMA)
# ===========================
@router.get("/{id_submission}", response_model=GradingOut)
def get_grading(
    id_submission: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    grading = db.query(Grading).filter(
        Grading.id_submission == id_submission
    ).first()

    if not grading:
        raise HTTPException(status_code=404, detail="Grading tidak ditemukan.")

    # Jika mahasiswa, cek akses
    if current_user.role == "mahasiswa":
        submission = db.query(Submission).filter(
            Submission.id_submission == id_submission,
            Submission.id_mahasiswa == current_user.id_user
        ).first()
        if not submission:
            raise HTTPException(status_code=403, detail="Akses ditolak.")

    return grading