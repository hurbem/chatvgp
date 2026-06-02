from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional
from datetime import datetime

class Condominio(Base):
    __tablename__ = "condominios"

    id: int = Column(Integer, primary_key=True, index=True)
    nome: str = Column(String(255), nullable=False, index=True)
    cidade: str = Column(String(100), nullable=False, index=True)
    criado_em: Optional[datetime] = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Condominio(id={self.id}, nome={self.nome}, cidade={self.cidade})>"
