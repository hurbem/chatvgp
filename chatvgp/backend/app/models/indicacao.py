from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Indicacao(Base):
    __tablename__ = "indicacoes"

    id = Column(Integer, primary_key=True, index=True)
    condominio_id = Column(Integer, ForeignKey("condominios.id"), nullable=False, index=True)
    nome_morador = Column(String(255), nullable=False)
    whatsapp_morador = Column(String(20), nullable=False)
    criado_em = Column(DateTime, server_default=func.now(), index=True)

    def __repr__(self):
        return f"<Indicacao(id={self.id}, morador={self.nome_morador}, condominio_id={self.condominio_id})>"
