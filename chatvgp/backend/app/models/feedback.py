from sqlalchemy import String, DateTime, ForeignKey, Text, Boolean, Date, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import mapped_column, relationship
from app.database import Base
from typing import Optional
from datetime import date, datetime

class Feedback(Base):
    __tablename__ = "feedbacks"

    id: int = mapped_column(primary_key=True, index=True)
    prestador_id: int = mapped_column(ForeignKey("prestadores.id"), nullable=False, index=True)
    condominio_id: int = mapped_column(ForeignKey("condominios.id"), nullable=False, index=True)
    categoria_id: int = mapped_column(ForeignKey("categorias.id"), nullable=False, index=True)
    data_feedback: date = mapped_column(Date, nullable=False)
    qualidade: int = mapped_column(nullable=False)  # 1-5
    material_estimativa: str = mapped_column(String(50), nullable=False)  # 'Acertou', 'Subestimou 10-25%', etc
    prazo_manteve: bool = mapped_column(Boolean, nullable=False)  # True/False
    custo_manteve: bool = mapped_column(Boolean, nullable=False)  # True/False
    observacoes: Optional[str] = mapped_column(Text, nullable=True)
    seu_feedback: bool = mapped_column(Boolean, default=False)
    criado_em: Optional[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=True)

    # Relationships
    prestador: Optional['Prestador'] = relationship("Prestador")
    condominio: Optional['Condominio'] = relationship("Condominio")
    categoria: Optional['Categoria'] = relationship("Categoria")

    def __repr__(self):
        return f"<Feedback(id={self.id}, prestador_id={self.prestador_id}, qualidade={self.qualidade})>"
