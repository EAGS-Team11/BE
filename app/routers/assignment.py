# app/routers/assignment.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db, get_current_active_user 
from app.models.assignments import Assignment
from app.models.user import User 
from app.schemas.assignment import AssignmentCreate, AssignmentOut

router = APIRouter(tags=["assignment"])

# 1. CREATE ASSIGNMENT
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
        deadline=assignment.deadline
    )
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

# 2. GET ASSIGNMENTS BY COURSE ID (ENDPOINT BARU)
@router.get("/course/{course_id}", response_model=List[AssignmentOut])
def get_assignments_by_course(
    course_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mengambil semua assignment berdasarkan ID Course"""
    assignments = db.query(Assignment).filter(Assignment.id_course == course_id).all()
    
    if not assignments:
        # Kita return list kosong saja, jangan error 404, supaya frontend tetap merender halaman
        return []
        
    return assignments