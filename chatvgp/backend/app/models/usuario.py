from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional
from datetime import datetime

class Usuario(Base):
    __tablename__ = "usuarios"

    id: int = mapped_column(primary_key=True, index=True)
    email: str = mapped_column(String(255), unique=True, nullable=False, index=True)
    senha_hash: str = mapped_column(String(255), nullable=False)
    nome: Optional[str] = mapped_column(String(255), nullable=True)
    criado_em: Optional[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=True)
    ativo: bool = mapped_column(Boolean, default=True)

    def __repr__(self):
        return f"<Usuario(id={self.id}, email={self.email})>"
