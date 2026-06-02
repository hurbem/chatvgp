from sqlalchemy import String, DateTime
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional
from datetime import datetime

class Condominio(Base):
    __tablename__ = "condominios"

    id: int = mapped_column(primary_key=True, index=True)
    nome: str = mapped_column(String(255), nullable=False, index=True)
    cidade: str = mapped_column(String(100), nullable=False, index=True)
    criado_em: Optional[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=True)

    def __repr__(self):
        return f"<Condominio(id={self.id}, nome={self.nome}, cidade={self.cidade})>"
