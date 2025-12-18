# app/routers/predict.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from decimal import Decimal
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.dependencies import get_db, get_current_active_user
from app.models.submissions import Submission
from app.models.grading import Grading
from app.models.user import User
from app.models.questions import Question

# ✅ pakai grader Gemini kamu
from app.utils.ai_grader import grader

router = APIRouter(tags=["predict"])


# =========================
# Request schemas
# =========================
class PredictSingleRequest(BaseModel):
    id_submission: int


class PredictBulkRequest(BaseModel):
    """
    Untuk menilai 1 mahasiswa pada 1 assignment (semua soal).
    """
    min_answer_len: int = 5  # optional guard


# =========================
# 1) PREVIEW AI grading 1 submission (per soal) - tidak simpan DB
# =========================
@router.post("/predict", response_model=Dict[str, Any])
def predict_one_submission(
    request: PredictSingleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(status_code=403, detail="Hanya dosen/admin yang dapat melakukan prediksi.")

    # Ambil submission
    sub = db.query(Submission).filter(Submission.id_submission == request.id_submission).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission tidak ditemukan.")

    # Ambil soal + bobot + kunci
    q = db.query(Question).filter(Question.id_question == sub.id_question).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question untuk submission ini tidak ditemukan.")

    # Nilai pakai LLM (0..bobot)
    result = grader.grade_essay(
        soal=q.teks_soal,
        kunci_jawaban=q.kunci_jawaban or "",
        jawaban_mahasiswa=sub.jawaban or "",
        max_score_dosen=float(q.bobot or 0)
    )

    return {
        "id_submission": sub.id_submission,
        "id_question": sub.id_question,
        "bobot": q.bobot,
        "skor_ai": result["final_score"],
        "feedback_ai": result["feedback"],
        "method": result.get("method", "-")
    }


# =========================
# 2) SIMPAN AI grading 1 submission (upsert) ke DB
# =========================
@router.post("/grade", response_model=Dict[str, Any])
def save_ai_grade_one_submission(
    request: PredictSingleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(status_code=403, detail="Hanya dosen/admin yang dapat menyimpan grading AI.")

    sub = db.query(Submission).filter(Submission.id_submission == request.id_submission).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission tidak ditemukan.")

    q = db.query(Question).filter(Question.id_question == sub.id_question).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question untuk submission ini tidak ditemukan.")

    result = grader.grade_essay(
        soal=q.teks_soal,
        kunci_jawaban=q.kunci_jawaban or "",
        jawaban_mahasiswa=sub.jawaban or "",
        max_score_dosen=float(q.bobot or 0)
    )

    try:
        existing = db.query(Grading).filter(Grading.id_submission == sub.id_submission).first()
        if existing:
            existing.skor_ai = Decimal(str(result["final_score"]))
            existing.feedback_ai = result["feedback"]
        else:
            db.add(Grading(
                id_submission=sub.id_submission,
                skor_ai=Decimal(str(result["final_score"])),
                feedback_ai=result["feedback"],
            ))

        db.commit()

        return {
            "id_submission": sub.id_submission,
            "id_question": sub.id_question,
            "bobot": q.bobot,
            "skor_ai": float(result["final_score"]),
            "feedback_ai": result["feedback"],
            "method": result.get("method", "-")
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan AI grading: {str(e)}")


# =========================
# 3) PREVIEW AI grading untuk SEMUA soal (1 assignment + 1 mahasiswa) - tidak simpan
# =========================
@router.post("/predict/assignment/{assignment_id}/student/{student_id}", response_model=List[Dict[str, Any]])
def predict_bulk_assignment_student(
    assignment_id: int,
    student_id: int,
    request: PredictBulkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(status_code=403, detail="Hanya dosen/admin.")

    subs = db.query(Submission).filter(
        Submission.id_assignment == assignment_id,
        Submission.id_mahasiswa == student_id
    ).all()

    if not subs:
        return []

    results: List[Dict[str, Any]] = []
    for sub in subs:
        q = db.query(Question).filter(Question.id_question == sub.id_question).first()
        if not q:
            continue

        result = grader.grade_essay(
            soal=q.teks_soal,
            kunci_jawaban=q.kunci_jawaban or "",
            jawaban_mahasiswa=sub.jawaban or "",
            max_score_dosen=float(q.bobot or 0)
        )

        results.append({
            "id_submission": sub.id_submission,
            "id_question": sub.id_question,
            "nomor_soal": q.nomor_soal,
            "bobot": q.bobot,
            "skor_ai": float(result["final_score"]),
            "feedback_ai": result["feedback"],
            "method": result.get("method", "-")
        })

    return results


# =========================
# 4) SIMPAN AI grading untuk SEMUA soal (1 assignment + 1 mahasiswa) - upsert
# =========================
@router.post("/grade/assignment/{assignment_id}/student/{student_id}", response_model=List[Dict[str, Any]])
def save_ai_grade_bulk_assignment_student(
    assignment_id: int,
    student_id: int,
    request: PredictBulkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(status_code=403, detail="Hanya dosen/admin.")

    subs = db.query(Submission).filter(
        Submission.id_assignment == assignment_id,
        Submission.id_mahasiswa == student_id
    ).all()

    if not subs:
        return []

    try:
        out: List[Dict[str, Any]] = []

        for sub in subs:
            q = db.query(Question).filter(Question.id_question == sub.id_question).first()
            if not q:
                continue

            result = grader.grade_essay(
                soal=q.teks_soal,
                kunci_jawaban=q.kunci_jawaban or "",
                jawaban_mahasiswa=sub.jawaban or "",
                max_score_dosen=float(q.bobot or 0)
            )

            existing = db.query(Grading).filter(Grading.id_submission == sub.id_submission).first()
            if existing:
                existing.skor_ai = Decimal(str(result["final_score"]))
                existing.feedback_ai = result["feedback"]
            else:
                db.add(Grading(
                    id_submission=sub.id_submission,
                    skor_ai=Decimal(str(result["final_score"])),
                    feedback_ai=result["feedback"]
                ))

            out.append({
                "id_submission": sub.id_submission,
                "id_question": sub.id_question,
                "nomor_soal": q.nomor_soal,
                "bobot": q.bobot,
                "skor_ai": float(result["final_score"]),
                "feedback_ai": result["feedback"],
                "method": result.get("method", "-")
            })

        db.commit()
        return out

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan AI grading bulk: {str(e)}")


# =========================
# 5) Statistik mahasiswa (berdasarkan skor_ai)
# =========================
@router.get("/my_stats")
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "mahasiswa":
        raise HTTPException(status_code=403, detail="Akses ditolak.")

    total_submitted = db.query(Submission).filter(
        Submission.id_mahasiswa == current_user.id_user
    ).count()

    graded_submissions = db.query(Submission).join(Grading).filter(
        Submission.id_mahasiswa == current_user.id_user
    )
    graded_count = graded_q.count()

    pending_submissions = db.query(Submission).outerjoin(Grading).filter(
        Submission.id_mahasiswa == current_user.id_user,
        Grading.id_grade.is_(None)
    )
    pending_count = pending_submissions.count()

    avg_score_decimal = graded_submissions.with_entities(
        sql_func.avg(Grading.skor_ai)
    ).scalar()

    avg_score = float(avg_score_decimal) if avg_score_decimal else 0.0

    return {
        "total_submitted": total_submitted,
        "graded_count": graded_count,
        "pending_count": pending_count,
        "average_score": round(avg_score, 1)
    }
