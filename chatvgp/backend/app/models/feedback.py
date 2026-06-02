from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    prestador_id = Column(Integer, ForeignKey("prestadores.id"), nullable=False, index=True)
    condominio_id = Column(Integer, ForeignKey("condominios.id"), nullable=False, index=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False, index=True)
    data_feedback = Column(Date, nullable=False)
    qualidade = Column(Integer, nullable=False)  # 1-5
    material_estimativa = Column(String(50), nullable=False)  # 'Acertou', 'Subestimou 10-25%', etc
    prazo_manteve = Column(Boolean, nullable=False)  # True/False
    custo_manteve = Column(Boolean, nullable=False)  # True/False
    observacoes = Column(Text, nullable=True)
    seu_feedback = Column(Boolean, default=False)
    criado_em = Column(DateTime, server_default=func.now())

    # Relationships
    prestador = relationship("Prestador")
    condominio = relationship("Condominio")
    categoria = relationship("Categoria")

    def __repr__(self):
        return f"<Feedback(id={self.id}, prestador_id={self.prestador_id}, qualidade={self.qualidade})>"
