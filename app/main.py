# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.database import Base, engine
from app.dependencies import create_database_if_not_exists

# Import router
from app.routers import auth, course, assignment, submission, predict, upload, grading

# 1. Buat database jika belum ada
create_database_if_not_exists()

# 2. Buat Tabel (Create Tables)
Base.metadata.create_all(bind=engine)

# --- Inisialisasi App ---
app = FastAPI(title="Essay Autograding API")

# --- UPDATE CONFIG CORS ---
origins = [
    "http://localhost:5173",      # Frontend Localhost
    "http://127.0.0.1:5173",      # Frontend IP
    "http://localhost:3000",      # Jaga-jaga jika pakai port React default
    "http://localhost",           # Jaga-jaga akses tanpa port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # Baris ini sudah diperbaiki (hanya satu)
    allow_credentials=True,
    allow_methods=["*"],          # Izinkan semua method (GET, POST, PUT, DELETE, dll)
    allow_headers=["*"],          # Izinkan semua header
)

# Custom OpenAPI (Swagger UI) untuk tombol Authorize
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

# --- Include Routers ---
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(course.router, prefix="/course", tags=["course"])
app.include_router(assignment.router, prefix="/assignment", tags=["assignment"])
app.include_router(submission.router, prefix="/submission", tags=["submission"])
app.include_router(predict.router, prefix="/predict", tags=["predict"])
app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(grading.router, prefix="/grading", tags=["grading"])