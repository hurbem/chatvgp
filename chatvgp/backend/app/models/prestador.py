from sqlalchemy import String, DateTime, ForeignKey, Text, ARRAY, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import mapped_column, relationship
from app.database import Base
from typing import List, Optional
from datetime import datetime

class Prestador(Base):
    __tablename__ = "prestadores"

    id: int = mapped_column(primary_key=True, index=True)
    nome: str = mapped_column(String(255), nullable=False, index=True)
    whatsapp: str = mapped_column(String(20), nullable=False)
    categoria_id: int = mapped_column(ForeignKey("categorias.id"), nullable=False, index=True)
    condominio_ids: List[int] = mapped_column(ARRAY(Integer), default=[], nullable=True)
    status: str = mapped_column(String(20), default="ativo", index=True)  # 'ativo', 'inativo'
    criado_em: Optional[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=True)
    notas: Optional[str] = mapped_column(Text, nullable=True)

    # Relationship
    categoria: Optional['Categoria'] = relationship("Categoria")

    def __repr__(self):
        return f"<Prestador(id={self.id}, nome={self.nome}, status={self.status})>"
