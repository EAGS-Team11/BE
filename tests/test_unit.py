# tests/test_unit.py

import pytest
from app.utils.auth import hash_password, verify_password, create_access_token
from app.utils.ai_grader import grader

def test_password_hashing_logic():
    password = "password_rahasia_123"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    assert verify_password("salah", hashed) is False

def test_token_creation():
    token = create_access_token(data={"sub": "2001"})
    assert isinstance(token, str)

def test_ai_grader_instance():
    # Memastikan Singleton AI Grader berhasil inisialisasi
    assert grader is not None
    assert grader.llm_model == "gemini-2.5-flash"