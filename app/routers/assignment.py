# app/routers/assignment.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.dependencies import get_db, get_current_active_user

from app.dependencies import get_db, get_current_active_user
from app.models.assignments import Assignment
from app.models.questions import Question
from app.models.submissions import Submission
from app.models.user import User

from app.schemas.assignment import AssignmentCreate, AssignmentOut, AssignmentWithQuestionsCreate

router = APIRouter(tags=["assignment"])


# ==========================================
# 1. CREATE ASSIGNMENT WITH QUESTIONS (FITUR UTAMA)
# ==========================================
@router.post("/create_with_questions", status_code=status.HTTP_201_CREATED)
def create_assignment_with_questions(
    payload: AssignmentWithQuestionsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya dosen atau admin yang dapat membuat assignment."
        )

    # ✅ total points dari semua bobot soal
    total_points = sum((q.bobot or 0) for q in payload.questions)
    if total_points <= 0:
        raise HTTPException(status_code=400, detail="Total points harus > 0. Pastikan bobot soal terisi.")

    try:
        # 1) Buat assignment header + points (INI FIX UTAMA)
        new_assignment = Assignment(
            judul=payload.judul,
            deskripsi=payload.deskripsi,
            deadline=payload.deadline,
            id_course=payload.id_course,
            created_by=current_user.id_user,
            points=total_points
        )
        db.add(new_assignment)
        db.flush()

        # 2) Buat questions
        for q in payload.questions:
            new_question = Question(
                id_assignment=new_assignment.id_assignment,
                nomor_soal=q.nomor_soal,
                teks_soal=q.teks_soal,
                bobot=q.bobot,
                kunci_jawaban=q.kunci_jawaban
            )
            db.add(new_question)

        db.commit()
        db.refresh(new_assignment)

        return {"message": "Assignment dan Soal berhasil dibuat", "id": new_assignment.id_assignment}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal membuat assignment: {str(e)}")


# ==========================================
# 2. GET SINGLE ASSIGNMENT / DETAIL
# ==========================================
@router.get("/{assignment_id}", response_model=AssignmentOut)
def get_assignment_detail(
    assignment_id: int,
    db: Session = Depends(get_db)
):
    assignment = db.query(Assignment).filter(Assignment.id_assignment == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment tidak ditemukan")

    total_count = (
        db.query(Submission.id_mahasiswa)
        .join(Question, Question.id_question == Submission.id_question)
        .filter(Question.id_assignment == assignment_id)
        .distinct()
        .count()
    )
    assignment.total_submitted = total_count

    return assignment


# ==========================================
# 3. GET ASSIGNMENTS BY COURSE ID
# ==========================================
@router.get("/course/{course_id}", response_model=List[AssignmentOut])
def get_assignments_by_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    assignments = db.query(Assignment).filter(Assignment.id_course == course_id).all()
    return assignments or []


# ==========================================
# 4. CREATE SIMPLE ASSIGNMENT (LEGACY)
# ==========================================
@router.post("/", response_model=AssignmentOut)
def create_assignment(
    assignment: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya dosen atau admin yang dapat membuat assignment."
        )

    db_assignment = Assignment(
        id_course=assignment.id_course,
        judul=assignment.judul,
        deskripsi=assignment.deskripsi,
        deadline=assignment.deadline,
        # ✅ minimal biar tidak null
        points=0,
        created_by=current_user.id_user
    )

    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)

    # 2. Simpan Loop Soal
    try:
        for q in payload.questions:
            new_question = Question(
                id_assignment=db_assignment.id_assignment, 
                nomor_soal=q.nomor_soal,
                teks_soal=q.teks_soal,
                kunci_jawaban=q.kunci_jawaban,
                bobot=q.bobot
            )
            db.add(new_question)
        
        db.commit()
        # Refresh dengan joinedload agar return response lengkap dengan questions
        db.refresh(db_assignment)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan soal: {str(e)}")

    return db_assignment


# ==========================================
# 5. UPDATE ASSIGNMENT (EDIT / PUT)
# ==========================================
@router.put("/{assignment_id}", response_model=AssignmentOut)
def update_assignment(
    assignment_id: int,
    payload: AssignmentWithQuestionsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(status_code=403, detail="Hanya dosen yang boleh mengedit.")

    assignment_db = db.query(Assignment).filter(Assignment.id_assignment == assignment_id).first()
    if not assignment_db:
        raise HTTPException(status_code=404, detail="Assignment tidak ditemukan")

    assignment_db.judul = payload.judul
    assignment_db.deskripsi = payload.deskripsi
    assignment_db.deadline = payload.deadline

    existing_questions = db.query(Question).filter(Question.id_assignment == assignment_id).all()
    existing_questions_map = {q.id_question: q for q in existing_questions}
    processed_ids = []

    for q_data in payload.questions:
        q_id = getattr(q_data, "id_question", None)

        if q_id and q_id in existing_questions_map:
            ex = existing_questions_map[q_id]
            ex.teks_soal = q_data.teks_soal
            ex.kunci_jawaban = q_data.kunci_jawaban
            ex.bobot = q_data.bobot
            ex.nomor_soal = q_data.nomor_soal
            processed_ids.append(q_id)
        else:
            new_q = Question(
                id_assignment=assignment_id,
                nomor_soal=q_data.nomor_soal,
                teks_soal=q_data.teks_soal,
                kunci_jawaban=q_data.kunci_jawaban,
                bobot=q_data.bobot
            )
            db.add(new_q)

    # delete question yang hilang (kalau aman)
    for ex_q in existing_questions:
        if ex_q.id_question not in processed_ids:
            has_submission = db.query(Submission).filter(Submission.id_question == ex_q.id_question).first()
            if not has_submission:
                db.delete(ex_q)

    try:
        # ✅ recompute points setelah update soal (pakai query aggregate)
        assignment_db.points = (
            db.query(func.coalesce(func.sum(Question.bobot), 0))
            .filter(Question.id_assignment == assignment_id)
            .scalar()
        )

        db.commit()
        db.refresh(assignment_db)

        total_count = (
            db.query(Submission.id_mahasiswa)
            .join(Question, Question.id_question == Submission.id_question)
            .filter(Question.id_assignment == assignment_id)
            .distinct()
            .count()
        )
        assignment_db.total_submitted = total_count

        return assignment_db

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan saat update: {str(e)}")
