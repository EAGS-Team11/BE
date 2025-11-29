# app/routers/submission.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_active_user 
from app.models.submissions import Submission
from app.models.user import User 
from app.schemas.submission import SubmissionCreate, SubmissionOut

router = APIRouter(tags=["submission"])

@router.post("/", response_model=SubmissionOut)
def submit_assignment(
    submission: SubmissionCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # Endpoing dilindungi
):
    # Logika verifikasi role (Hanya Mahasiswa)
    if current_user.role != "mahasiswa":
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Hanya mahasiswa yang dapat mengirimkan tugas.")

    # Menggunakan ID user asli dari token
    db_submission = Submission(
        id_assignment=submission.id_assignment,
        id_mahasiswa=current_user.id_user, 
        jawaban=submission.jawaban
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission