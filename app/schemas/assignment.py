from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AssignmentCreate(BaseModel):
    id_course: int
    judul: str
    deskripsi: Optional[str] = None
    deadline: Optional[datetime] = None

class AssignmentOut(BaseModel):
    id_assignment: int
    id_course: int
    judul: str
    deskripsi: Optional[str]
    deadline: Optional[datetime]

    class Config:
        orm_mode = True