# app/models/system_logs.py
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.sql import func

class SystemLog(Base):
    __tablename__ = "system_logs"

    id_log = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id_user"), nullable=True)
    aksi = Column(String(255))
    timestamp = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User")