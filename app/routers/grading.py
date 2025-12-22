# app/routers/grading.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.dependencies import get_db, get_current_active_user
from app.models.grading import Grading
from app.models.user import User
from app.models.submissions import Submission
from app.schemas.grading import GradingOut

router = APIRouter(tags=["grading"])

# Schema untuk Input Penilaian Dosen
class GradingInput(BaseModel):
    id_submission: int
    nilai: float
    feedback: Optional[str] = None

@router.get("/assignment/{assignment_id}/student/{student_id}", response_model=List[GradingOut])
def get_student_grades(
    assignment_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Verifikasi akses: Dosen, Admin, atau Mahasiswa yang bersangkutan
    if current_user.role not in ["dosen", "admin", "mahasiswa"]:
        raise HTTPException(status_code=403, detail="Akses ditolak.")
    
    if current_user.role == "mahasiswa" and current_user.id_user != student_id:
        raise HTTPException(status_code=403, detail="Anda tidak diizinkan melihat nilai orang lain.")

    # Ambil nilai berdasarkan relasi submission
    results = (
        db.query(Grading)
        .join(Submission, Submission.id_submission == Grading.id_submission)
        .filter(
            Submission.id_assignment == assignment_id,
            Submission.id_mahasiswa == student_id
        )
        .all()
    )
    
    # PERBAIKAN: Kembalikan list kosong [] jika belum ada nilai, jangan 404 agar FE tidak crash
    return results if results else []

@router.post("/grade_submission", status_code=status.HTTP_201_CREATED)
def grade_submission_bulk(
    payload: List[GradingInput],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Hanya Dosen atau Admin yang boleh menyimpan nilai
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(status_code=403, detail="Hanya dosen/admin yang boleh menilai.")

    graded_count = 0
    try:
        for item in payload:
            # Cari apakah sudah ada data grading (dari AI atau input sebelumnya)
            existing_grade = db.query(Grading).filter(
                Grading.id_submission == item.id_submission
            ).first()

            if existing_grade:
                # LOGIKA UPSERT: Jika sudah ada, Update field Dosen
                # Field AI (skor_ai, feedback_ai) tetap aman di kolomnya masing-masing
                existing_grade.skor_dosen = item.nilai
                existing_grade.feedback_dosen = item.feedback or ""
            else:
                # Jika belum ada record sama sekali, buat baru
                new_grade = Grading(
                    id_submission=item.id_submission,
                    skor_dosen=item.nilai,
                    feedback_dosen=item.feedback or ""
                )
                db.add(new_grade)

            graded_count += 1

        db.commit()
        return {
            "message": "Nilai berhasil disimpan atau diperbarui", 
            "total_graded": graded_count
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan nilai: {str(e)}")

# Endpoint khusus untuk menghapus nilai (jika diperlukan)
@router.delete("/submission/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_grade(
    submission_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(status_code=403, detail="Akses ditolak.")
        
    grade = db.query(Grading).filter(Grading.id_submission == submission_id).first()
    if grade:
        db.delete(grade)
        db.commit()
    return None