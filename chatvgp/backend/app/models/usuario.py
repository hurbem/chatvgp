from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional
from datetime import datetime

class Usuario(Base):
    __tablename__ = "usuarios"

    id: int = Column(Integer, primary_key=True, index=True)
    email: str = Column(String(255), unique=True, nullable=False, index=True)
    senha_hash: str = Column(String(255), nullable=False)
    nome: Optional[str] = Column(String(255))
    criado_em: Optional[datetime] = Column(DateTime, server_default=func.now())
    ativo: bool = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Usuario(id={self.id}, email={self.email})>"
