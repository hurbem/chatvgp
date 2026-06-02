from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from typing import List, Optional

class Prestador(Base):
    __tablename__ = "prestadores"

    id: int = Column(Integer, primary_key=True, index=True)
    nome: str = Column(String(255), nullable=False, index=True)
    whatsapp: str = Column(String(20), nullable=False)
    categoria_id: int = Column(Integer, ForeignKey("categorias.id"), nullable=False, index=True)
    condominio_ids: List[int] = Column(ARRAY(Integer), default=[])
    status: str = Column(String(20), default="ativo", index=True)  # 'ativo', 'inativo'
    criado_em: Optional[DateTime] = Column(DateTime, server_default=func.now())
    notas: Optional[str] = Column(Text)

    # Relationship
    categoria: Optional['Categoria'] = relationship("Categoria")

    def __repr__(self):
        return f"<Prestador(id={self.id}, nome={self.nome}, status={self.status})>"
