# File: BE/app/schemas/submission.py

from pydantic import BaseModel, ConfigDict
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from typing import Optional, List
from decimal import Decimal
from app.schemas.user import UserOut 

# --- SCHEMA BARU UNTUK MENANGANI LIST JAWABAN (INPUT) ---
class SubmissionItem(BaseModel):
    id_question: int
    jawaban: str

class SubmissionCreate(BaseModel):
    id_assignment: int
    items: List[SubmissionItem] 
# ------------------------------------------------

# Schema untuk Assignment (Subset)
class AssignmentInfo(BaseModel):
    id_assignment: int
    judul: str
    deskripsi: Optional[str] = None
    deadline: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# Schema untuk Grading (Subset)
class GradingInfo(BaseModel):
    skor_ai: Optional[Decimal] = None
    skor_dosen: Optional[Decimal] = None
    feedback_ai: Optional[str] = None
    graded_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class SubmissionDetailOut(BaseModel):
    """Schema Gabungan untuk menampilkan Submission + Grading + Assignment"""
    id_submission: int
    jawaban: str
    submitted_at: datetime
    
    # Relasi
    assignment: AssignmentInfo
    grading: Optional[GradingInfo] = None 
    mahasiswa: Optional[UserOut] = None 
    
    model_config = ConfigDict(from_attributes=True)

class SubmissionOut(BaseModel):
    id_submission: int
    id_assignment: int
    id_question: int
    id_mahasiswa: int
    jawaban: str
    submitted_at: datetime
    id_question: int # Penting untuk mapping di frontend

    model_config = ConfigDict(from_attributes=True)

# --- SCHEMA UNTUK LIST MAHASISWA DI HALAMAN DOSEN ---
class SubmissionStudentListOut(BaseModel):
    id_mahasiswa: int
    nama_mahasiswa: str
    submitted_at: datetime
    status_grading: str # "Sudah Dinilai" atau "Belum Dinilai"
    
    model_config = ConfigDict(from_attributes=True)

# --- [BARU] SCHEMA UNTUK RIWAYAT ESSAY MAHASISWA (MY ESSAYS) ---
class MySubmissionOut(BaseModel):
    id_assignment: int
    judul_assignment: str
    nama_course: str
    submitted_at: datetime
    status: str       # "Graded" atau "Submitted"
    nilai: float      # Rata-rata atau Total nilai
    
    model_config = ConfigDict(from_attributes=True)