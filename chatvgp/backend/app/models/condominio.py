from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Condominio(Base):
    __tablename__ = "condominios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False, index=True)
    cidade = Column(String(100), nullable=False, index=True)
    criado_em = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Condominio(id={self.id}, nome={self.nome}, cidade={self.cidade})>"
