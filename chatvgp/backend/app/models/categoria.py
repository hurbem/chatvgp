from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=True, nullable=False, index=True)
    descricao = Column(Text, nullable=True)
    aliases = Column(String(500), nullable=True)  # Palavras-chave para busca
    ordem = Column(Integer, nullable=False, default=999)  # Ordem de apresentação

    def __repr__(self):
        return f"<Categoria(id={self.id}, nome={self.nome})>"
