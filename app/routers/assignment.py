from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db, get_current_active_user
from app.models.assignments import Assignment
from app.models.user import User
from app.schemas.assignment import (
    AssignmentCreate,
    AssignmentStudentOut,
    AssignmentTeacherOut
)

router = APIRouter(tags=["assignment"])

# ============================================================
# 1. CREATE ASSIGNMENT (khusus dosen/admin)
# ============================================================
@router.post("/", response_model=AssignmentTeacherOut)
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
        soal=assignment.soal,
        kunci_jawaban=assignment.kunci_jawaban,
        points=assignment.points,
        deadline=assignment.deadline,
    )

    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)

    return db_assignment


# ============================================================
# 2. GET ASSIGNMENTS BY COURSE (role-based output)
# ============================================================
@router.get("/course/{course_id}")
def get_assignments_by_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    assignments = db.query(Assignment).filter(
        Assignment.id_course == course_id
    ).all()

    if current_user.role == "mahasiswa":
        # Hide kunci jawaban untuk mahasiswa
        return [
            AssignmentStudentOut.model_validate(a) for a in assignments
        ]

    # untuk dosen/admin
    return [
        AssignmentTeacherOut.model_validate(a) for a in assignments
    ]
