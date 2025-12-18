# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.database import Base, engine

# ==============================================================================
# [PENTING] IMPORT SEMUA MODEL DI SINI
# Agar Base.metadata.create_all mengenali tabel dan membuatnya otomatis
# ==============================================================================
from app.models.user import User
from app.models.course import Course
from app.models.assignments import Assignment
from app.models.questions import Question
from app.models.submissions import Submission
from app.models.grading import Grading
# ==============================================================================

from app.routers import auth, course, assignment, submission, predict, upload, grading 
from app.dependencies import create_database_if_not_exists, get_db 

# 1. Buat Database jika belum ada
create_database_if_not_exists()

# 2. Buat Tabel (Create Tables)
# Karena model sudah di-import di atas, perintah ini akan membuat 
# tabel assignments, questions, dll dengan struktur TERBARU.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Essay Autograding API")

# ==========================================
# SETTING CORS
# ==========================================
origins = [
    "http://localhost:5173",    # Port Frontend Default Vite
    "http://127.0.0.1:5173",    # Alternatif IP Frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ==========================================

# Tambahkan security scheme Bearer pada OpenAPI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
        description="API untuk Essay Autograding",
        routes=app.routes,
    )

    components = openapi_schema.setdefault("components", {})
    security_schemes = components.setdefault("securitySchemes", {})
    security_schemes["bearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }

    openapi_schema.setdefault("security", []).append({"bearerAuth": []})

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

@app.get("/")
def root():
    return {"message": "FastAPI Essay Autograding API is running"}

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(course.router, prefix="/course", tags=["course"])
app.include_router(assignment.router, prefix="/assignment", tags=["assignment"])
app.include_router(submission.router, prefix="/submission", tags=["submission"])
app.include_router(predict.router, prefix="/predict", tags=["predict"])
app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(grading.router, prefix="/grading", tags=["grading"])