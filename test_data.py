#!/usr/bin/env python3
"""Create test data for endpoint testing"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, engine
from decimal import Decimal

# Import all models to ensure they're registered
from app.models import user, course, course_enroll, assignments, submissions, grading
from app.models.submissions import Submission
from app.models.grading import Grading

# Connect to db
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = SessionLocal()
try:
    # Create test submission
    test_submission = Submission(
        id_assignment=1,
        id_mahasiswa=6,  # mahasiswa user id
        jawaban="Kecerdasan buatan telah mengubah cara kita bekerja dan hidup. Dalam essay ini, saya akan membahas isu-isu etika yang penting dalam pengembangan dan implementasi AI. Pertama, keadilan dan bias dalam algoritma AI sangat kritis. Kedua, privasi pengguna harus dilindungi dengan ketat. Ketiga, transparansi dalam pengambilan keputusan AI diperlukan. Keempat, dampak sosial terhadap pekerjaan dan ketidaksetaraan harus dipertimbangkan. Kelima, akuntabilitas untuk kesalahan AI harus jelas. Dalam kesimpulannya, kita perlu kerangka kerja etika yang kuat untuk memastikan AI dikembangkan untuk kebaikan umat manusia."
    )
    db.add(test_submission)
    db.commit()
    print(f"✅ Created test submission: ID={test_submission.id_submission}")
    
    # Create test grading  
    test_grading = Grading(
        id_submission=test_submission.id_submission,
        skor_ai=Decimal("75.50"),
        feedback_ai="Good essay with solid structure"
    )
    db.add(test_grading)
    db.commit()
    print(f"✅ Created test grading: ID={test_grading.id_grade}")
    
finally:
    db.close()
    print("✅ Test data created successfully")
