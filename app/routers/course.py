# app/routers/course.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.models.user import User
from app.models.course import Course
from app.models.course_enroll import CourseEnroll
from app.schemas.course import CourseCreate, CourseOut
from app.schemas.course_enroll import CourseEnrollCreate, CourseEnrollOut
from app.dependencies import get_db, get_current_active_user

router = APIRouter(tags=["course"])

@router.post("/", response_model=CourseOut)
def create_course(
    course: CourseCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user) # MELINDUNGI ENDPOINT
):
    # Logika verifikasi role (Hanya Dosen yang bisa membuat course)
    if current_user.role != "dosen" and current_user.role != "admin":
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya dosen atau admin yang dapat membuat course."
        )

    db_course = Course(
        kode_course=course.kode_course,
        nama_course=course.nama_course,
        access_code=course.access_code,
        id_dosen=current_user.id_user # MENGGUNAKAN ID USER ASLI
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@router.get("/", response_model=list[CourseOut])
def get_all_courses(db: Session = Depends(get_db)):
    """Get all courses (public endpoint, no auth required)."""
    courses = db.query(Course).all()
    return courses

@router.post("/join", response_model=CourseEnrollOut)
def join_course(
    enroll: CourseEnrollCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # MELINDUNGI ENDPOINT
):
    # Logika verifikasi role (Hanya Mahasiswa yang boleh join)
    if current_user.role != "mahasiswa":
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya mahasiswa yang dapat bergabung ke course."
        )

    # Ganti hardcode id_mahasiswa = 2 dengan ID user dari token
    db_enroll = CourseEnroll(
        id_course=enroll.id_course,
        id_mahasiswa=current_user.id_user # MENGGUNAKAN ID USER ASLI
    )
    db.add(db_enroll)
    db.commit()
    db.refresh(db_enroll)
    return db_enroll

# 1. Endpoint GET Course untuk Dosen
@router.get("/dosen", response_model=list[CourseOut])
def get_dosen_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in ["dosen", "admin"]:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akses ditolak.")

    # Mengambil semua course yang id_dosen nya sama dengan user yang login
    courses = db.query(Course).filter(Course.id_dosen == current_user.id_user).all()
    return courses

# 2. Endpoint GET Course untuk Mahasiswa (My Courses)
@router.get("/my", response_model=list[CourseOut])
def get_my_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "mahasiswa":
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akses ditolak.")

    # Mengambil semua enrollment untuk user ini
    enrollments = db.query(CourseEnroll).filter(
        CourseEnroll.id_mahasiswa == current_user.id_user
    ).options(joinedload(CourseEnroll.course)).all() # Load Course secara bersamaan

    # Ekstrak objek Course dari Enrollment
    courses = [enroll.course for enroll in enrollments]
    return courses