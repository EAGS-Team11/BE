# File: BE/app/routers/submission.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.dependencies import get_db, get_current_active_user
from app.models.submissions import Submission
from app.models.user import User
from app.models.assignments import Assignment
from app.models.questions import Question
from app.models.grading import Grading
from app.schemas.submission import (
    SubmissionCreate, 
    SubmissionResponse, 
    SubmissionDetailOut
)

# AI GRADER
from app.utils.ai_grader import grader

# --- INI YANG HILANG SEBELUMNYA ---
router = APIRouter(tags=["submission"])
# ----------------------------------

# ============================================================
# 1. SUBMIT TUGAS (MULTI-SOAL + AUTO GRADING)
# ============================================================
@router.post("/", response_model=SubmissionResponse)
def submit_assignment(
    payload: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "mahasiswa":
        raise HTTPException(status_code=403, detail="Hanya mahasiswa yang dapat mengirimkan tugas.")

    # Cek Assignment
    assignment = db.query(Assignment).filter(
        Assignment.id_assignment == payload.id_assignment
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment tidak ditemukan.")

    count_success = 0
    
    for item in payload.items:
        # Ambil data soal
        question = db.query(Question).filter(
            Question.id_question == item.id_question,
            Question.id_assignment == payload.id_assignment 
        ).first()

        if not question:
            continue 

        # Cek Existing Submission (Update jika ada)
        existing_sub = db.query(Submission).filter(
            Submission.id_assignment == payload.id_assignment,
            Submission.id_question == item.id_question,
            Submission.id_mahasiswa == current_user.id_user
        ).first()

        if existing_sub:
            existing_sub.jawaban = item.jawaban
            db_submission = existing_sub
        else:
            db_submission = Submission(
                id_assignment=payload.id_assignment,
                id_question=item.id_question,
                id_mahasiswa=current_user.id_user,
                jawaban=item.jawaban
            )
            db.add(db_submission)
        
        db.flush() 

        # --- AI GRADING ---
        try:
            # Hapus nilai lama
            db.query(Grading).filter(Grading.id_submission == db_submission.id_submission).delete()

            hasil_ai = grader.grade_essay(
                soal=question.teks_soal,           
                kunci_jawaban=question.kunci_jawaban or "",
                jawaban_mahasiswa=item.jawaban,
                max_score_dosen=float(question.bobot)
            )

            new_grading = Grading(
                id_submission=db_submission.id_submission,
                skor_ai=hasil_ai.get("final_score", 0),
                feedback_ai=hasil_ai.get("feedback", "Tidak ada feedback AI"),
                technical_score=hasil_ai.get("technical_score", 0),
                llm_score=hasil_ai.get("llm_score", 0),
                # Skor dosen masih kosong saat submit
                skor_dosen=None,
                feedback_dosen=None
            )
            db.add(new_grading)
            count_success += 1

        except Exception as e:
            print(f"❌ Error Grading Soal ID {item.id_question}: {e}")
            pass 

    db.commit()

    return {
        "message": "Jawaban berhasil disimpan dan dinilai.",
        "submitted_count": count_success
    }


# ============================================================
# 2. LIST SUBMISSION BY ASSIGNMENT (DOSEN VIEW)
# ============================================================
@router.get("/assignment/{assignment_id}/submissions", response_model=List[SubmissionDetailOut])
def list_assignment_submissions(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Cek Role
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(status_code=403, detail="Akses ditolak.")

    # Cek Assignment
    assignment = db.query(Assignment).filter(Assignment.id_assignment == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment tidak ditemukan.")

    # Ambil Submission + Relasi
    submissions = db.query(Submission).filter(
        Submission.id_assignment == assignment_id
    ).options(
        joinedload(Submission.mahasiswa),
        joinedload(Submission.grading),
        joinedload(Submission.question),
        joinedload(Submission.assignment)
    ).all()

    return submissions


# ============================================================
# 3. LIST MY SUBMISSIONS (MAHASISWA VIEW)
# ============================================================
@router.get("/my", response_model=List[SubmissionDetailOut])
def list_my_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    submissions = db.query(Submission).filter(
        Submission.id_mahasiswa == current_user.id_user
    ).options(
        joinedload(Submission.grading),
        joinedload(Submission.question),
        joinedload(Submission.assignment)
    ).all()

    return submissions