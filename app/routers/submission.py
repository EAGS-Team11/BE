# app/routers/submission.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.submissions import Submission
from app.schemas.submission import SubmissionCreate, SubmissionOut

router = APIRouter(tags=["submission"])

@router.post("/", response_model=SubmissionOut)
def submit_assignment(submission: SubmissionCreate, db: Session = Depends(get_db)):
    # sementara hardcode id_mahasiswa = 2
    db_submission = Submission(
        id_assignment=submission.id_assignment,
        id_mahasiswa=2,
        jawaban=submission.jawaban
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission