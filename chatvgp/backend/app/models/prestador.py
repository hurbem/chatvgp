from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Prestador(Base):
    __tablename__ = "prestadores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False, index=True)
    whatsapp = Column(String(20), nullable=False)
    instagram = Column(String(500), nullable=True)  # URL do perfil Instagram
    site = Column(String(500), nullable=True)  # Endereço web
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False, index=True)
    status = Column(String(20), default="ativo", index=True)  # 'ativo', 'inativo'
    criado_em = Column(DateTime, server_default=func.now())
    notas = Column(Text, nullable=True)

    # Relationship
    categoria = relationship("Categoria")

    def __repr__(self):
        return f"<Prestador(id={self.id}, nome={self.nome}, status={self.status})>"
