from pydantic import BaseModel
from datetime import datetime

class SubmissionCreate(BaseModel):
    id_assignment: int
    jawaban: str

class SubmissionOut(BaseModel):
    id_submission: int
    id_assignment: int
    id_mahasiswa: int
    jawaban: str
    submitted_at: datetime

    class Config:
        orm_mode = True