from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Prestador(Base):
    __tablename__ = "prestadores"

    # Identificação
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True, unique=True, index=True)
    whatsapp = Column(String(20), nullable=False, unique=True, index=True)
    cpf_cnpj = Column(String(20), nullable=True, unique=True, index=True)
    descricao = Column(Text, nullable=True)

    # Contato
    instagram = Column(String(500), nullable=True)
    site = Column(String(500), nullable=True)

    # Badges (você controla)
    verificado_hurbem = Column(Boolean, default=False)
    premium = Column(Boolean, default=False)

    # Status e Auditoria
    status = Column(String(20), default="ativo", index=True)
    criado_em = Column(DateTime, server_default=func.now())
    atualizado_em = Column(DateTime, server_default=func.now(), onupdate=func.now())
    notas = Column(Text, nullable=True)

    # Relação many-to-many com categorias
    categorias = relationship(
        "Categoria",
        secondary="prestador_categorias",
        backref="prestadores"
    )

    def __repr__(self):
        return f"<Prestador(id={self.id}, nome={self.nome}, status={self.status})>"
