# BE/app/routers/submission.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.dependencies import get_db, get_current_active_user
from app.models.submissions import Submission
from app.models.user import User
from app.models.grading import Grading
from app.models.questions import Question
from app.models.assignments import Assignment
from app.models.course import Course

from app.schemas.submission import (
    SubmissionCreate,
    SubmissionOut,
    MySubmissionOut
)

router = APIRouter(tags=["submission"])
# ----------------------------------

# ==========================================
# 1. MAHASISWA SUBMIT JAWABAN
# ==========================================
@router.post("/", status_code=status.HTTP_201_CREATED)
def submit_answers(
    payload: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "mahasiswa":
        raise HTTPException(status_code=403, detail="Hanya mahasiswa yang bisa submit.")

    saved_count = 0

    for item in payload.items:
        existing_submission = db.query(Submission).filter(
            Submission.id_mahasiswa == current_user.id_user,
            Submission.id_question == item.id_question
        ).first()

        if existing_submission:
            existing_submission.jawaban = item.jawaban
        else:
            new_submission = Submission(
                id_assignment=payload.id_assignment,
                id_mahasiswa=current_user.id_user,
                id_question=item.id_question,
                jawaban=item.jawaban
            )
            db.add(new_submission)

        saved_count += 1

    try:
        db.commit()
        return {"message": "Jawaban berhasil dikirim", "total_saved": saved_count}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan jawaban: {str(e)}")


# ==========================================
# 2. DOSEN LIHAT LIST MAHASISWA YG SUBMIT
# ==========================================
@router.get("/assignment/{assignment_id}/submissions", response_model=List[Dict[str, Any]])
def get_assignment_submissions(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(status_code=403, detail="Akses ditolak.")

    student_ids = (
        db.query(Submission.id_mahasiswa)
        .filter(Submission.id_assignment == assignment_id)
        .distinct()
        .all()
    )

    result_list = []

    for (s_id,) in student_ids:
        student = db.query(User).filter(User.id_user == s_id).first()
        if not student:
            continue

        last_sub = db.query(Submission).filter(
            Submission.id_assignment == assignment_id,
            Submission.id_mahasiswa == s_id
        ).order_by(Submission.submitted_at.desc()).first()

        grading_records = (
            db.query(Grading)
            .join(Submission)
            .filter(
                Submission.id_assignment == assignment_id,
                Submission.id_mahasiswa == s_id
            )
            .all()
        )

        is_graded = len(grading_records) > 0
        status_text = "Sudah Dinilai" if is_graded else "Belum Dinilai"

        total_score = 0
        if is_graded:
            total_score = sum(g.skor_dosen for g in grading_records if g.skor_dosen is not None)

        result_list.append({
            "id_mahasiswa": student.id_user,
            "nama_mahasiswa": student.nama,
            "submitted_at": last_sub.submitted_at if last_sub else None,
            "status_grading": status_text,
            "total_score": total_score
        })

    return result_list


# ==========================================
# 3. GET DETAIL JAWABAN MAHASISWA (Check Answer)
# ==========================================
@router.get("/assignment/{assignment_id}/student/{student_id}", response_model=List[SubmissionOut])
def get_student_submissions(
    assignment_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(status_code=403, detail="Akses ditolak.")

    submissions = db.query(Submission).filter(
        Submission.id_assignment == assignment_id,
        Submission.id_mahasiswa == student_id
    ).all()

    return submissions


# ==========================================
# 4. GET "MY ESSAYS" (Riwayat Mahasiswa)
# ==========================================
@router.get("/my", response_model=List[MySubmissionOut])
def get_my_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "mahasiswa":
        raise HTTPException(status_code=403, detail="Hanya mahasiswa.")

    assignment_ids = (
        db.query(Submission.id_assignment)
        .filter(Submission.id_mahasiswa == current_user.id_user)
        .distinct()
        .all()
    )

    results = []

    for (aid,) in assignment_ids:
        assignment = db.query(Assignment).filter(Assignment.id_assignment == aid).first()
        if not assignment:
            continue

        course = db.query(Course).filter(Course.id_course == assignment.id_course).first()
        course_name = course.nama_course if course else "Unknown Course"

        last_sub = db.query(Submission).filter(
            Submission.id_assignment == aid,
            Submission.id_mahasiswa == current_user.id_user
        ).order_by(Submission.submitted_at.desc()).first()

        grades = (
            db.query(Grading)
            .join(Submission)
            .filter(
                Submission.id_assignment == aid,
                Submission.id_mahasiswa == current_user.id_user
            )
            .all()
        )

        final_score = 0
        status_text = "Submitted"

        if grades:
            total_score = sum(g.skor_dosen for g in grades if g.skor_dosen)
            final_score = total_score
            status_text = "Graded"

        results.append({
            "id_assignment": assignment.id_assignment,
            "judul_assignment": assignment.judul,
            "nama_course": course_name,
            "submitted_at": last_sub.submitted_at if last_sub else None,
            "status": status_text,
            "nilai": float(final_score)
        })

    return results


# ==========================================
# 5. GET "MY SUBMISSION DETAIL" (Detail jawaban + nilai per soal)
# ==========================================
@router.get("/my/{assignment_id}/detail", response_model=List[Dict[str, Any]])
def get_my_submission_detail(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "mahasiswa":
        raise HTTPException(status_code=403, detail="Hanya mahasiswa.")

    # Ambil assignment
    assignment = db.query(Assignment).filter(Assignment.id_assignment == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment tidak ditemukan.")

    # Ambil jawaban mahasiswa
    submissions = db.query(Submission).filter(
        Submission.id_assignment == assignment_id,
        Submission.id_mahasiswa == current_user.id_user
    ).all()

    # Ambil grading mahasiswa
    grades = (
        db.query(Grading)
        .join(Submission)
        .filter(
            Submission.id_assignment == assignment_id,
            Submission.id_mahasiswa == current_user.id_user
        )
        .all()
    )

    # Bikin map biar lookup cepat
    submission_by_qid = {s.id_question: s for s in submissions}
    grade_by_subid = {g.id_submission: g for g in grades}

    # Pastikan assignment punya relasi questions
    questions = getattr(assignment, "questions", None)
    if questions is None:
        raise HTTPException(status_code=500, detail="Relasi assignment.questions tidak tersedia di model.")

    result = []
    for q in questions:
        sub = submission_by_qid.get(q.id_question)
        grade = grade_by_subid.get(sub.id_submission) if sub else None

        result.append({
            "nomor_soal": getattr(q, "nomor_soal", None),
            "pertanyaan": getattr(q, "teks_soal", None),
            "bobot_maks": getattr(q, "bobot", 0),
            "jawaban_kamu": sub.jawaban if sub else "-",
            "nilai_dosen": grade.skor_dosen if (grade and grade.skor_dosen is not None) else 0,
            "feedback_dosen": grade.feedback_dosen if (grade and grade.feedback_dosen) else "-",
            "status_nilai": "Sudah Dinilai" if grade else "Belum Dinilai"
        })

    return result
