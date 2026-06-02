from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from typing import Optional
from datetime import date, datetime

class Feedback(Base):
    __tablename__ = "feedbacks"

    id: int = Column(Integer, primary_key=True, index=True)
    prestador_id: int = Column(Integer, ForeignKey("prestadores.id"), nullable=False, index=True)
    condominio_id: int = Column(Integer, ForeignKey("condominios.id"), nullable=False, index=True)
    categoria_id: int = Column(Integer, ForeignKey("categorias.id"), nullable=False, index=True)
    data_feedback: date = Column(Date, nullable=False)
    qualidade: int = Column(Integer, nullable=False)  # 1-5
    material_estimativa: str = Column(String(50), nullable=False)  # 'Acertou', 'Subestimou 10-25%', etc
    prazo_manteve: bool = Column(Boolean, nullable=False)  # True/False
    custo_manteve: bool = Column(Boolean, nullable=False)  # True/False
    observacoes: Optional[str] = Column(Text)
    seu_feedback: bool = Column(Boolean, default=False)
    criado_em: Optional[datetime] = Column(DateTime, server_default=func.now())

    # Relationships
    prestador: Optional['Prestador'] = relationship("Prestador")
    condominio: Optional['Condominio'] = relationship("Condominio")
    categoria: Optional['Categoria'] = relationship("Categoria")

    def __repr__(self):
        return f"<Feedback(id={self.id}, prestador_id={self.prestador_id}, qualidade={self.qualidade})>"
