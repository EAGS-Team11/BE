from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal
from app.dependencies import get_db, get_current_active_user
from app.models.grading import Grading
from app.models.submissions import Submission
from app.models.user import User
from app.schemas.grading import GradingCreate, GradingOut

router = APIRouter(tags=["grading"])

# ===========================
# Manual grading oleh dosen/admin
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
# Ambil grading by submission
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
