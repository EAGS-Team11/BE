from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

# ======================================================
# INPUT SCHEMA (CREATE)
# ======================================================
class AssignmentCreate(BaseModel):
    id_course: int
    judul: str
    deskripsi: Optional[str] = None
    soal: Optional[str] = None
    kunci_jawaban: Optional[str] = None
    points: int  # wajib
    deadline: Optional[datetime] = None


# ======================================================
# OUTPUT UNTUK MAHASISWA (tanpa kunci jawaban)
# ======================================================
class AssignmentStudentOut(BaseModel):
    id_assignment: int
    id_course: int
    judul: str
    deskripsi: Optional[str]
    soal: Optional[str]
    points: Optional[int]  # bisa None
    deadline: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ======================================================
# OUTPUT UNTUK DOSEN/ADMIN (lengkap)
# ======================================================
class AssignmentTeacherOut(BaseModel):
    id_assignment: int
    id_course: int
    judul: str
    deskripsi: Optional[str]
    soal: Optional[str]
    kunci_jawaban: Optional[str]
    points: Optional[int]  # bisa None
    deadline: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

    # validator untuk default points 0 jika None
    @field_validator("points", mode="before")
    def default_points(cls, v):
        if v is None:
            return 0
        return v
