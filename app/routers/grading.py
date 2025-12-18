# app/routers/grading.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.dependencies import get_db, get_current_active_user
from app.models.grading import Grading
from app.models.user import User
from app.models.submissions import Submission

from pydantic import BaseModel

# ✅ pakai schema output yang rapi
from app.schemas.grading import GradingOut

router = APIRouter(tags=["grading"])


# =========================
# Schema input bulk grading
# =========================
class GradingInput(BaseModel):
    id_submission: int
    nilai: float
    feedback: Optional[str] = None


# ============================================================
# GET: Ambil nilai mahasiswa per assignment (AI + Dosen)
# ============================================================
@router.get(
    "/assignment/{assignment_id}/student/{student_id}",
    response_model=List[GradingOut]
)
def get_student_grades(
    assignment_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(status_code=403, detail="Akses ditolak.")

    results = (
        db.query(Grading)
        .join(Submission, Submission.id_submission == Grading.id_submission)
        .filter(
            Submission.id_assignment == assignment_id,
            Submission.id_mahasiswa == student_id
        )
        .all()
    )

    return results or []


# ============================================================
# POST: Save bulk grading DOSEN (UPSERT)
# - penting: jangan ganggu skor_ai & feedback_ai
# ============================================================
@router.post("/grade_submission", status_code=status.HTTP_201_CREATED)
def grade_submission_bulk(
    payload: List[GradingInput],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(status_code=403, detail="Hanya dosen/admin yang boleh menilai.")

    graded_count = 0

    try:
        for item in payload:
            submission = db.query(Submission).filter(
                Submission.id_submission == item.id_submission
            ).first()
            if not submission:
                continue

            existing_grade = db.query(Grading).filter(
                Grading.id_submission == item.id_submission
            ).first()

            if existing_grade:
                # ✅ update hanya field dosen
                existing_grade.skor_dosen = item.nilai
                existing_grade.feedback_dosen = item.feedback or ""
            else:
                # ✅ bikin record baru (AI fields null dulu, aman)
                db.add(Grading(
                    id_submission=item.id_submission,
                    skor_dosen=item.nilai,
                    feedback_dosen=item.feedback or ""
                ))

            graded_count += 1

        db.commit()
        return {"message": "Nilai berhasil disimpan/diperbarui", "total_graded": graded_count}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan nilai: {str(e)}")
