# app/routers/submission.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.dependencies import get_db, get_current_active_user
from app.models.submissions import Submission
from app.models.user import User
from app.models.assignments import Assignment
from app.models.grading import Grading
from app.schemas.submission import SubmissionCreate, SubmissionOut, SubmissionDetailOut

# AI GRADER
from app.utils.ai_grader import grader

router = APIRouter(tags=["submission"])


# ============================================================
# 1. SUBMIT TUGAS + AUTO GRADING
# ============================================================
@router.post("/", response_model=SubmissionOut)
def submit_assignment(
    submission: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):

    # hanya mahasiswa yang boleh submit
    if current_user.role != "mahasiswa":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya mahasiswa yang dapat mengirimkan tugas."
        )

    # ambil data assignment
    assignment = db.query(Assignment).filter(
        Assignment.id_assignment == submission.id_assignment
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment tidak ditemukan.")

    # simpan submission
    db_submission = Submission(
        id_assignment=submission.id_assignment,
        id_mahasiswa=current_user.id_user,
        jawaban=submission.jawaban
    )

    db.add(db_submission)
    db.flush()  # untuk dapat id_submission

    # ============================================================
    # AI GRADING
    # ============================================================
    try:
        hasil_ai = grader.grade_essay(
            soal=assignment.soal,                     # FIX: question → soal
            kunci_jawaban=assignment.kunci_jawaban or "",
            jawaban_mahasiswa=submission.jawaban,
            max_score_dosen=100.0                     # karena DB kamu tidak punya points
        )

        # simpan hasil grading
        new_grading = Grading(
            id_submission=db_submission.id_submission,
            grade=hasil_ai["final_score"],
            feedback=hasil_ai["feedback"],
            technical_score=hasil_ai["technical_score"],
            llm_score=hasil_ai["llm_score"]
        )
        db.add(new_grading)

    except Exception as e:
        print(f"❌ Error AI Grading: {e}")
        # submission tetap masuk meskipun AI gagal
        pass

    db.commit()
    db.refresh(db_submission)

    return db_submission


# ============================================================
# 2. LIST SUBMISSION SAYA (Mahasiswa)
# ============================================================
@router.get("/my", response_model=list[SubmissionDetailOut])
def list_my_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "mahasiswa":
        raise HTTPException(status_code=403, detail="Akses ditolak.")

    submissions = db.query(Submission).filter(
        Submission.id_mahasiswa == current_user.id_user
    ).options(
        joinedload(Submission.assignment),
        joinedload(Submission.grading)
    ).all()

    return submissions


# ============================================================
# 3. LIST SUBMISSION PER ASSIGNMENT (Dosen/Admin)
# ============================================================
@router.get("/assignment/{assignment_id}/submissions", response_model=list[SubmissionDetailOut])
def list_assignment_submissions(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(status_code=403, detail="Akses ditolak.")

    assignment = db.query(Assignment).filter(
        Assignment.id_assignment == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment tidak ditemukan.")

    # dosen hanya boleh akses assignment miliknya
    if current_user.role == "dosen" and assignment.course.id_dosen != current_user.id_user:
        raise HTTPException(status_code=403, detail="Anda tidak memiliki akses ke assignment ini.")

    submissions = db.query(Submission).filter(
        Submission.id_assignment == assignment_id
    ).options(
        joinedload(Submission.mahasiswa),
        joinedload(Submission.grading)
    ).all()

    return submissions
