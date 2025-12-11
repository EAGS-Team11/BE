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
    # --- PERUBAHAN: MENGHAPUS PEMBATASAN ROLE MAHASISWA ---
    # Logika verifikasi role LAMA:
    # if current_user.role != "mahasiswa":
    #      raise HTTPException(
    #          status_code=status.HTTP_403_FORBIDDEN,
    #          detail="Hanya mahasiswa yang dapat bergabung ke course."
    #      )
    # Course Enrollment tetap akan mencatat 'id_mahasiswa' (sebenarnya id_user)
    # dari pengguna yang login (bisa Dosen, bisa Mahasiswa).
    
    # Ganti hardcode id_mahasiswa = 2 dengan ID user dari token
    db_enroll = CourseEnroll(
        id_course=enroll.id_course,
        id_mahasiswa=current_user.id_user # MENGGUNAKAN ID USER ASLI (ID Dosen atau Mahasiswa)
    )
    db.add(db_enroll)
    db.commit()
    db.refresh(db_enroll)
    return db_enroll
# --- AKHIR PERUBAHAN ---

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
    # --- PERBAIKAN DI SINI ---
    # Hilangkan pengecekan role yang membatasi hanya 'mahasiswa'
    # if current_user.role != "mahasiswa":
    #      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akses ditolak.")
    # --------------------------

    enrollments = db.query(CourseEnroll).filter(
        CourseEnroll.id_mahasiswa == current_user.id_user # Menggunakan ID user yang login (Dosen/Mhs)
    ).options(joinedload(CourseEnroll.course)).all() 

    # Ekstrak objek Course dari Enrollment
    courses = [enroll.course for enroll in enrollments]
    return courses

# --- ENDPOINT BARU 3: EDIT COURSE (PUT) ---
@router.put("/{course_id}", response_model=CourseOut)
def update_course(
    course_id: int,
    course_update: CourseCreate, # Reuse CourseCreate schema for update
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 1. Verifikasi Role
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya dosen atau admin yang dapat mengubah course."
        )

    # 2. Cari Course
    course = db.query(Course).filter(Course.id_course == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course tidak ditemukan."
        )

    # 3. Verifikasi Kepemilikan (Kecuali Admin)
    if course.id_dosen != current_user.id_user and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki hak untuk mengubah course ini."
        )

    # 4. Update Data
    course.kode_course = course_update.kode_course
    course.nama_course = course_update.nama_course
    course.access_code = course_update.access_code
    
    db.commit()
    db.refresh(course)
    return course

# --- ENDPOINT BARU 4: DELETE COURSE (DELETE) ---
@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 1. Verifikasi Role
    if current_user.role not in ["dosen", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya dosen atau admin yang dapat menghapus course."
        )

    # 2. Cari Course
    course = db.query(Course).filter(Course.id_course == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course tidak ditemukan."
        )

    # 3. Verifikasi Kepemilikan (Kecuali Admin)
    if course.id_dosen != current_user.id_user and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki hak untuk menghapus course ini."
        )

    # 4. Lakukan Pengecekan Integritas Data (Foreign Key Constraint)
    try:
        # Hapus Enrollment terkait course ini (diperlukan jika CASCADE tidak aktif)
        db.query(CourseEnroll).filter(CourseEnroll.id_course == course_id).delete()
        
        # Hapus Course utama (Asumsi CASCADE DELETE aktif di model Course -> Assignments)
        db.delete(course)
        db.commit()
        
    except Exception as e:
        # Catch error Foreign Key
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menghapus course. Pastikan semua assignment, submission, dan grading terkait telah dihapus. Error: {e}"
        )

    return {"message": "Course berhasil dihapus."}