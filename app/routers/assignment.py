# app/routers/assignment.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models.assignments import Assignment
from app.schemas.assignment import AssignmentCreate, AssignmentOut

router = APIRouter(tags=["assignment"])

@router.post("/", response_model=AssignmentOut)
def create_assignment(assignment: AssignmentCreate, db: Session = Depends(get_db)):
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