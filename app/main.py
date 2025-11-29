# app/main.py

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.database import Base, engine
from app.routers import auth, course, assignment, submission, predict, upload
from app.dependencies import create_database_if_not_exists, get_db # <-- Impor ini

# Panggil fungsi ini SEBELUM membuat tabel
create_database_if_not_exists()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Essay Autograding API")


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