from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from app.database import Base

class PrestadorCategoria(Base):
    __tablename__ = "prestador_categorias"

    id = Column(Integer, primary_key=True, index=True)
    prestador_id = Column(Integer, ForeignKey("prestadores.id"), nullable=False, index=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False, index=True)

    # Garantir que não haja duplicatas (um prestador + uma categoria só uma vez)
    __table_args__ = (
        UniqueConstraint('prestador_id', 'categoria_id', name='uq_prestador_categoria'),
    )

    def __repr__(self):
        return f"<PrestadorCategoria(prestador_id={self.prestador_id}, categoria_id={self.categoria_id})>"
