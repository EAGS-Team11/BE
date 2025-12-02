# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.database import Base, engine
# --- PERUBAHAN 1: Tambahkan 'grading' di sini ---
from app.routers import auth, course, assignment, submission, predict, upload, grading 
from app.dependencies import create_database_if_not_exists, get_db 

# Panggil fungsi ini SEBELUM membuat tabel
create_database_if_not_exists()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Essay Autograding API")

# ==========================================
# SETTING CORS (Agar Frontend Bisa Masuk)
# ==========================================
origins = [
    "http://localhost:5173",    # Port Frontend Default Vite
    "http://127.0.0.1:5173",    # Alternatif IP Frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # Izinkan alamat di atas
    allow_credentials=True,
    allow_methods=["*"],        # Izinkan semua method (GET, POST, PUT, DELETE)
    allow_headers=["*"],        # Izinkan semua header (Authorization, Content-Type)
)
# ==========================================

# Tambahkan security scheme Bearer pada OpenAPI agar Swagger Authorize menerima token paste
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
        description="API untuk Essay Autograding",
        routes=app.routes,
    )

    # Tambah skema keamanan HTTP bearer
    components = openapi_schema.setdefault("components", {})
    security_schemes = components.setdefault("securitySchemes", {})
    security_schemes["bearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }

    # Atur skema keamanan global (opsional)
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

# --- PERUBAHAN 2: Daftarkan Router Grading ---
app.include_router(grading.router, prefix="/grading", tags=["grading"])