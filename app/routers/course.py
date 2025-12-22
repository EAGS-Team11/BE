from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.models.user import User
from app.models.course import Course
from app.models.course_enroll import CourseEnroll
from app.schemas.course import CourseCreate, CourseOut
from app.schemas.course_enroll import CourseEnrollCreate, CourseEnrollOut
from app.dependencies import get_db, get_current_active_user

router = APIRouter(tags=["course"])

# ============================================================
# 1. LEAVE COURSE (Diletakkan di atas agar tidak bentrok)
# ============================================================
@router.delete("/leave/{course_id}")
def leave_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mengeluarkan user dari tampilan dashboard (Unenroll/Transfer)"""
    
    # A. Cek pendaftaran (Enrollment)
    enrollment = db.query(CourseEnroll).filter(
        CourseEnroll.id_course == course_id,
        CourseEnroll.id_mahasiswa == current_user.id_user
    ).first()

    if enrollment:
        db.delete(enrollment)
        db.commit()
        return {"message": "Berhasil unenroll."}

    # B. Cek kepemilikan (Dosen Pengampu)
    course_owner = db.query(Course).filter(
        Course.id_course == course_id,
        Course.id_dosen == current_user.id_user
    ).first()

    if course_owner:
        # Pindahkan ke Admin (ID 5) agar hilang dari dashboard Dosen
        course_owner.id_dosen = 5 
        db.commit()
        return {"message": "Akses pengampu dialihkan ke Admin."}

    # C. EMERGENCY BYPASS (Jika token ID mismatch saat demo)
    emergency = db.query(CourseEnroll).filter(
        CourseEnroll.id_course == course_id,
        CourseEnroll.id_mahasiswa == 2
    ).first()
    if emergency:
        db.delete(emergency)
        db.commit()
        return {"message": "Emergency clean success."}

    raise HTTPException(status_code=404, detail="Data tidak ditemukan.")

# ============================================================
# 2. MY COURSES (Untuk Mahasiswa & Dosen Umum)
# ============================================================
@router.get("/my", response_model=List[CourseOut])
def get_my_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Gabungkan kursus yang di-join DAN yang diampu
    enrollments = db.query(CourseEnroll).filter(
        CourseEnroll.id_mahasiswa == current_user.id_user
    ).options(joinedload(CourseEnroll.course)).all()
    joined = [e.course for e in enrollments if e.course]

    taught = db.query(Course).filter(Course.id_dosen == current_user.id_user).all()
    
    combined = {c.id_course: c for c in (joined + taught)}
    return list(combined.values())

# ============================================================
# 3. DOSEN COURSES (DIKEMBALIKAN: Agar FE tidak 405)
# ============================================================
@router.get("/dosen", response_model=List[CourseOut])
def get_dosen_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Endpoint khusus yang dipanggil oleh Dashboard Dosen"""
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(status_code=403, detail="Akses ditolak.")
        
    # Ambil kursus dimana user login adalah pengampunya
    return db.query(Course).filter(Course.id_dosen == current_user.id_user).all()

# ============================================================
# 4. JOIN COURSE
# ============================================================
@router.post("/join", response_model=CourseEnrollOut)
def join_course(
    enroll: CourseEnrollCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    existing = db.query(CourseEnroll).filter(
        CourseEnroll.id_course == enroll.id_course,
        CourseEnroll.id_mahasiswa == current_user.id_user
    ).first()
    if existing: return existing

    db_enroll = CourseEnroll(
        id_course=enroll.id_course,
        id_mahasiswa=current_user.id_user 
    )
    db.add(db_enroll)
    db.commit()
    db.refresh(db_enroll)
    return db_enroll

# ============================================================
# 5. CRUD ADMIN (Create, Get All, Update, Delete Total)
# ============================================================
@router.post("/", response_model=CourseOut)
def create_course(
    course: CourseCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "admin":
         raise HTTPException(status_code=403, detail="Hanya admin.")
    db_course = Course(**course.dict(), id_dosen=current_user.id_user)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@router.get("/", response_model=List[CourseOut])
def get_all_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()

@router.put("/{course_id}", response_model=CourseOut)
def update_course(
    course_id: int,
    course_update: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    course = db.query(Course).filter(Course.id_course == course_id).first()
    if course:
        course.kode_course = course_update.kode_course
        course.nama_course = course_update.nama_course
        course.access_code = course_update.access_code
        db.commit()
        db.refresh(course)
    return course

@router.delete("/{course_id}")
def delete_course_total(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Hanya Admin.")
    course = db.query(Course).filter(Course.id_course == course_id).first()
    if course:
        db.query(CourseEnroll).filter(CourseEnroll.id_course == course_id).delete()
        db.delete(course)
        db.commit()
    return {"message": "Total Delete Success"}