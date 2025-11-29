# app/utils/scoring.py

"""
Scoring utility module untuk menghitung skor otomatis essay.
Algorithm: Kombinasi sederhana dari:
  - Word count (20%)
  - Sentence structure (20%)
  - Keyword presence (30%)
  - Grammar/readability proxy (30%)
"""

import re
from typing import Tuple


def calculate_essay_score(
    essay_text: str,
    keywords: list[str] | None = None,
    min_words: int = 100,
    max_words: int = 5000
) -> Tuple[float, str]:
    """
    Hitung skor essay (0-100) berdasarkan berbagai metrik.
    
    Args:
        essay_text: Text essay yang dinilai
        keywords: List keyword yang harus ada (optional)
        min_words: Minimal word count untuk full score
        max_words: Maksimal word count (penality jika lebih)
    
    Returns:
        Tuple[score (0-100), feedback (string)]
    """
    
    if not essay_text or len(essay_text.strip()) == 0:
        return 0.0, "Essay kosong, tidak bisa dinilai."
    
    essay_text = essay_text.strip()
    feedback_parts = []
    scores = {}
    
    # 1. Word Count Score (20%)
    words = essay_text.split()
    word_count = len(words)
    
    if word_count < 50:
        word_score = max(0, (word_count / 50) * 50)
        feedback_parts.append(f"Jumlah kata terlalu sedikit ({word_count} kata, target minimal 100).")
    elif word_count < min_words:
        word_score = ((word_count - 50) / (min_words - 50)) * 100
        feedback_parts.append(f"Jumlah kata masih kurang ({word_count} kata, target {min_words}).")
    elif word_count > max_words:
        word_score = max(50, 100 - ((word_count - max_words) / 1000))
        feedback_parts.append(f"Jumlah kata terlalu banyak ({word_count} kata, batas maksimal {max_words}).")
    else:
        word_score = 100
    
    scores['word_count'] = word_score
    
    # 2. Sentence Structure Score (20%)
    # Hitung jumlah kalimat dan rata-rata panjang per kalimat
    sentences = re.split(r'[.!?]+', essay_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) == 0:
        sentence_score = 0
        feedback_parts.append("Tidak ada kalimat yang lengkap ditemukan.")
    else:
        avg_sentence_length = word_count / len(sentences)
        
        # Ideal: 10-20 kata per kalimat
        if avg_sentence_length < 5:
            sentence_score = (avg_sentence_length / 5) * 50
            feedback_parts.append("Kalimat terlalu pendek, struktur kurang kompleks.")
        elif avg_sentence_length < 10:
            sentence_score = 60
            feedback_parts.append("Struktur kalimat bisa lebih variatif.")
        elif avg_sentence_length <= 20:
            sentence_score = 100
        else:
            sentence_score = max(50, 100 - ((avg_sentence_length - 20) / 30) * 50)
            feedback_parts.append("Beberapa kalimat terlalu panjang, pertimbangkan untuk dipecah.")
    
    scores['sentence_structure'] = sentence_score
    
    # 3. Keyword Matching Score (30%)
    if keywords:
        keyword_score = 0
        found_keywords = []
        
        essay_lower = essay_text.lower()
        for keyword in keywords:
            if keyword.lower() in essay_lower:
                keyword_score += 1
                found_keywords.append(keyword)
        
        # Convert to 0-100 scale
        keyword_score = (keyword_score / len(keywords)) * 100 if keywords else 50
        scores['keyword_match'] = keyword_score
        
        if found_keywords:
            feedback_parts.append(f"Kata kunci ditemukan: {', '.join(found_keywords)}")
        else:
            feedback_parts.append("Tidak ada kata kunci yang ditemukan. Pastikan menggunakan term spesifik.")
    else:
        # Default 70 jika keywords tidak tersedia
        scores['keyword_match'] = 70
    
    # 4. Grammar/Readability Proxy Score (30%)
    # Heuristic sederhana: cek kehadiran common grammar patterns dan capitalization
    grammar_score = 50  # baseline
    
    # Cek capitalization (kalimat dimulai dengan huruf besar)
    capital_sentences = sum(1 for s in sentences if s and s[0].isupper())
    capitalization_ratio = capital_sentences / len(sentences) if sentences else 0
    
    if capitalization_ratio > 0.8:
        grammar_score += 30
    elif capitalization_ratio > 0.5:
        grammar_score += 15
    
    # Cek kehadiran tanda baca
    punctuation_count = len(re.findall(r'[.,;:\-]', essay_text))
    if punctuation_count > word_count * 0.05:  # Minimal 5% dari word count
        grammar_score += 10
    
    # Cek kehadiran common connecting words
    connectors = ['dan', 'atau', 'namun', 'tetapi', 'karena', 'oleh karena itu', 'sebagai hasil', 'lebih lanjut', 'however', 'moreover', 'therefore']
    connector_count = sum(1 for conn in connectors if conn.lower() in essay_lower)
    
    if connector_count > 0:
        grammar_score = min(100, grammar_score + (connector_count * 5))
    
    grammar_score = min(100, grammar_score)
    scores['grammar_readability'] = grammar_score
    
    # 5. Final Score Calculation (weighted average)
    final_score = (
        scores['word_count'] * 0.20 +
        scores['sentence_structure'] * 0.20 +
        scores['keyword_match'] * 0.30 +
        scores['grammar_readability'] * 0.30
    )
    
    final_score = round(final_score, 2)
    
    # Build feedback
    feedback = "\n".join(feedback_parts) if feedback_parts else "Essay memenuhi standar dasar."
    feedback += f"\n\nSkor Detail:\n- Word Count: {scores['word_count']:.1f}/100\n- Sentence Structure: {scores['sentence_structure']:.1f}/100\n- Keyword Match: {scores['keyword_match']:.1f}/100\n- Grammar/Readability: {scores['grammar_readability']:.1f}/100"
    
    return final_score, feedback


def get_feedback_level(score: float) -> str:
    """Kategori feedback berdasarkan score."""
    if score >= 85:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 50:
        return "Fair"
    else:
        return "Needs Improvement"
