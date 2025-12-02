# BE/app/routers/grading.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_active_user
from app.models.grading import Grading
from app.models.user import User
from app.models.submissions import Submission
from pydantic import BaseModel

router = APIRouter(tags=["grading"])

class GradingCreate(BaseModel):
    id_submission: int
    nilai: int
    feedback: str = None

@router.post("/", status_code=status.HTTP_201_CREATED)
def grade_submission(
    grade_data: GradingCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Cek Role Dosen
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(status_code=403, detail="Hanya dosen yang boleh menilai.")

    # Cek apakah submission ada
    submission = db.query(Submission).filter(Submission.id_submission == grade_data.id_submission).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission tidak ditemukan.")

    # Cek apakah sudah pernah dinilai?
    existing_grade = db.query(Grading).filter(Grading.id_submission == grade_data.id_submission).first()

    if existing_grade:
        # UPDATE NILAI (Pakai nama kolom yang benar: skor_dosen)
        existing_grade.skor_dosen = grade_data.nilai
        existing_grade.feedback_dosen = grade_data.feedback
        
        db.commit()
        db.refresh(existing_grade)
        return existing_grade
    else:
        # BUAT NILAI BARU (Pakai nama kolom yang benar: skor_dosen)
        new_grade = Grading(
            id_submission=grade_data.id_submission,
            skor_dosen=grade_data.nilai,      # <--- Disesuaikan
            feedback_dosen=grade_data.feedback # <--- Disesuaikan
        )
        db.add(new_grade)
        db.commit()
        db.refresh(new_grade)
        return new_grade