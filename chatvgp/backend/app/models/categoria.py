from sqlalchemy import String, Text
from sqlalchemy.orm import mapped_column, declarative_base
from app.database import Base
from typing import Optional

class Categoria(Base):
    __tablename__ = "categorias"

    id: int = mapped_column(primary_key=True, index=True)
    nome: str = mapped_column(String(100), unique=True, nullable=False, index=True)
    descricao: Optional[str] = mapped_column(Text, nullable=True)

    def __repr__(self):
        return f"<Categoria(id={self.id}, nome={self.nome})>"
