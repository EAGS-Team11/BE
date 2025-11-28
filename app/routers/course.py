# app/routers/course.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.course import Course
from app.models.course_enroll import CourseEnroll
from app.schemas.course import CourseCreate, CourseOut
from app.schemas.course_enroll import CourseEnrollCreate, CourseEnrollOut

router = APIRouter(tags=["course"])

@router.post("/", response_model=CourseOut)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    # sementara hardcode id_dosen = 1
    db_course = Course(
        kode_course=course.kode_course,
        nama_course=course.nama_course,
        access_code=course.access_code,
        id_dosen=1
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@router.post("/join", response_model=CourseEnrollOut)
def join_course(enroll: CourseEnrollCreate, db: Session = Depends(get_db)):
    # sementara hardcode id_mahasiswa = 2
    db_enroll = CourseEnroll(
        id_course=enroll.id_course,
        id_mahasiswa=2
    )
    db.add(db_enroll)
    db.commit()
    db.refresh(db_enroll)
    return db_enroll