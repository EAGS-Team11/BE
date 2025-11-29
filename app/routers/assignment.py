# app/routers/assignment.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_active_user 
from app.models.assignments import Assignment
from app.models.user import User 
from app.schemas.assignment import AssignmentCreate, AssignmentOut

router = APIRouter(tags=["assignment"])

@router.post("/", response_model=AssignmentOut)
def create_assignment(
    assignment: AssignmentCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # Endpoint dilindungi
):
    # Logika verifikasi role (Hanya Dosen/Admin)
    if current_user.role not in ["dosen", "admin"]:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya dosen atau admin yang dapat membuat assignment."
        )
    
    
    # Asumsi: Assignment hanya dapat dibuat oleh dosen yang memiliki course tersebut.
    # Namun, karena Course ID ada di payload, kita biarkan logic sederhana dulu.

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