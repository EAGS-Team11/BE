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
        orm_mode = True