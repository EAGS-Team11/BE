from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Question(Base):
    __tablename__ = "questions"

    id_question = Column(Integer, primary_key=True, index=True)
    
    # Menghubungkan Soal ke Assignment (Parent)
    # Tambahkan ondelete="CASCADE" agar jika Assignment dihapus, soal ikut terhapus
    id_assignment = Column(Integer, ForeignKey("assignments.id_assignment", ondelete="CASCADE"), nullable=False)
    
    nomor_soal = Column(Integer)  # Urutan soal (1, 2, 3...)
    teks_soal = Column(Text, nullable=False) # Pertanyaannya
    
    # Saya sarankan nullable=True untuk jaga-jaga, tapi False juga oke jika wajib diisi
    kunci_jawaban = Column(Text, nullable=True) 
    
    bobot = Column(Integer, default=10) # Nilai per soal

    # Relasi balik ke Parent (Assignment)
    assignment = relationship("Assignment", back_populates="questions")

    # --- TAMBAHAN PENTING ---
    # Relasi ke Submission (Jawaban Mahasiswa)
    # Ini diperlukan karena di model Submission kita pakai back_populates="question"
    submissions = relationship("Submission", back_populates="question", cascade="all, delete-orphan")