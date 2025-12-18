from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from typing import List

from app.dependencies import get_db, get_current_active_user
from app.models.assignments import Assignment
from app.models.questions import Question
from app.models.user import User
from app.schemas.assignment import (
    AssignmentCreate,
    AssignmentStudentOut,
    AssignmentTeacherOut
)

router = APIRouter(tags=["assignment"])

# ============================================================
# 1. CREATE ASSIGNMENT WITH QUESTIONS
# URL: POST /assignment/create_with_questions
# ============================================================
@router.post("/create_with_questions", response_model=AssignmentTeacherOut)
def create_assignment_with_questions(
    payload: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Cek Role Dosen/Admin
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(status_code=403, detail="Akses ditolak.")

    # Hitung total points otomatis dari bobot soal
    total_points = sum(q.bobot for q in payload.questions)

    # 1. Simpan Header Assignment
    db_assignment = Assignment(
        id_course=payload.id_course,
        judul=payload.judul,
        deskripsi=payload.deskripsi,
        start_date=payload.start_date,       # Kolom Baru
        task_type=payload.task_type,         # Kolom Baru
        time_duration=payload.time_duration, # Kolom Baru
        points=total_points,
        deadline=payload.deadline,
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


# ============================================================
# 2. GET ASSIGNMENTS BY COURSE (LIST)
# URL: GET /assignment/course/{course_id}
# ============================================================
@router.get("/course/{course_id}")
def get_assignments_by_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Ambil semua assignment DAN load relasi questions (untuk hitung jumlah soal di FE)
    assignments = db.query(Assignment).filter(
        Assignment.id_course == course_id
    ).options(
        joinedload(Assignment.questions) # <--- PENTING: Agar field 'questions' tidak kosong
    ).all()

    # --- LOGIC FILTER UNTUK MAHASISWA ---
    if current_user.role == "mahasiswa":
        valid_assignments = []
        current_time = datetime.now()

        for task in assignments:
            # Logic: Sembunyikan jika Deadline sudah lewat
            # (Sementara dimatikan agar Anda bisa test tugas lama)
            # if task.deadline and current_time > task.deadline:
            #     continue 
            
            valid_assignments.append(task)
        
        # Return format mahasiswa (Tanpa Kunci Jawaban)
        return [AssignmentStudentOut.model_validate(a) for a in valid_assignments]

    # Untuk Dosen/Admin: Tampilkan Semua
    return [AssignmentTeacherOut.model_validate(a) for a in assignments]


# ============================================================
# 3. GET ASSIGNMENT DETAIL (BY ID) -> PENTING UNTUK 'DO ASSIGNMENT'
# URL: GET /assignment/{assignment_id}
# ============================================================
@router.get("/{assignment_id}")
def get_assignment_detail(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Cari assignment berdasarkan ID DAN load relasi questions
    assignment = db.query(Assignment).filter(
        Assignment.id_assignment == assignment_id
    ).options(
        joinedload(Assignment.questions) # <--- PENTING: Solusi error "reading forEach/map" di Frontend
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment tidak ditemukan")

    # LOGIC ROLE:
    # Jika Mahasiswa -> Pakai Schema Student (Kunci Jawaban disembunyikan)
    if current_user.role == "mahasiswa":
        return AssignmentStudentOut.model_validate(assignment)

    # Jika Dosen -> Pakai Schema Teacher (Ada Kunci Jawaban)
    return AssignmentTeacherOut.model_validate(assignment)