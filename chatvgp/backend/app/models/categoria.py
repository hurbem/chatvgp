from sqlalchemy import Column, Integer, String, Text
from app.database import Base
from typing import Optional

class Categoria(Base):
    __tablename__ = "categorias"

    id: int = Column(Integer, primary_key=True, index=True)
    nome: str = Column(String(100), unique=True, nullable=False, index=True)
    descricao: Optional[str] = Column(Text)

    def __repr__(self):
        return f"<Categoria(id={self.id}, nome={self.nome})>"
