# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_db

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c