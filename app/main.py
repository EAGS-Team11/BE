# app/main.py
from fastapi import FastAPI
from app.database import Base, engine
from app.routers import auth, course, assignment, submission, predict, upload

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Essay Autograding API")

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