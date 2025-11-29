#!/usr/bin/env python3
"""Test scoring algorithm"""

from app.utils.scoring import calculate_essay_score, get_feedback_level

# Test scoring algorithm
essay = """Kecerdasan buatan telah mengubah cara kita bekerja dan hidup. Dalam essay ini, saya akan membahas isu-isu etika yang penting dalam pengembangan dan implementasi AI. Pertama, keadilan dan bias dalam algoritma AI sangat kritis. Kedua, privasi pengguna harus dilindungi dengan ketat. Ketiga, transparansi dalam pengambilan keputusan AI diperlukan. Keempat, dampak sosial terhadap pekerjaan dan ketidaksetaraan harus dipertimbangkan. Kelima, akuntabilitas untuk kesalahan AI harus jelas. Dalam kesimpulannya, kita perlu kerangka kerja etika yang kuat untuk memastikan AI dikembangkan untuk kebaikan umat manusia."""

keywords = ["AI", "ethics", "privacy", "fairness"]

score, feedback = calculate_essay_score(essay, keywords=keywords, min_words=100)
level = get_feedback_level(score)

print(f"Score: {score}/100")
print(f"Level: {level}")
print(f"\nFeedback:\n{feedback}")
