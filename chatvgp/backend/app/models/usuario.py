from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    nome = Column(String(255), nullable=True)
    criado_em = Column(DateTime, server_default=func.now())
    ativo = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Usuario(id={self.id}, email={self.email})>"
