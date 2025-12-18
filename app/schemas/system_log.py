# app/schemas/system_log.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SystemLogCreate(BaseModel):
    id_user: Optional[int]
    aksi: str

class SystemLogOut(BaseModel):
    id_log: int
    id_user: Optional[int]
    aksi: str
    timestamp: datetime

    class Config:
        from_attributes = True