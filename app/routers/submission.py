# app/routers/submission.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload 
from app.dependencies import get_db, get_current_active_user
from app.models.submissions import Submission
from app.models.user import User
from app.models.assignments import Assignment
from app.models.grading import Grading
from app.schemas.submission import SubmissionCreate, SubmissionOut, SubmissionDetailOut # <-- TAMBAH SUBMISSION DETAIL OUT
from app.schemas.grading import GradingOut # Diperlukan untuk Grading

router = APIRouter(tags=["submission"])

@router.post("/", response_model=SubmissionOut)
def submit_assignment(
    submission: SubmissionCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) 
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

# --- 1. GET /submission/my (List semua submission user Mahasiswa) ---
@router.get("/my", response_model=list[SubmissionDetailOut])
def list_my_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "mahasiswa":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akses ditolak.")

    submissions = db.query(Submission).filter(
        Submission.id_mahasiswa == current_user.id_user
    ).options(
        joinedload(Submission.assignment), 
        joinedload(Submission.grading)     
    ).all()
    
    return submissions

# --- 2. GET /assignment/{id_assignment}/submissions (List submissions untuk Dosen) ---
@router.get("/assignment/{assignment_id}/submissions", response_model=list[SubmissionDetailOut])
def list_assignment_submissions(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akses ditolak.")
    
    # Ambil Assignment untuk verifikasi kepemilikan (Penting untuk security)
    assignment = db.query(Assignment).filter(Assignment.id_assignment == assignment_id).first()
    if not assignment or (assignment.course.id_dosen != current_user.id_user and current_user.role != "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Anda tidak memiliki akses ke assignment ini.")

    
    submissions = db.query(Submission).filter(
        Submission.id_assignment == assignment_id
    ).options(
        joinedload(Submission.mahasiswa),  
        joinedload(Submission.grading)
    ).all()
    
    return submissions