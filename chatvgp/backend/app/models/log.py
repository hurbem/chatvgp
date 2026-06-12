from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base
from datetime import datetime

class Log(Base):
    """
    Modelo para armazenar logs de pesquisas e eventos da aplicação.
    """
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(100), index=True)  # "CATEGORIA_NAO_IDENTIFICADA", "BUSCA_SUCESSO", etc
    pergunta = Column(Text, nullable=True)  # A pergunta do usuário
    categoria_encontrada = Column(String(255), nullable=True)  # Categoria encontrada (se houver)
    mensagem = Column(Text, nullable=True)  # Mensagem adicional
    criado_em = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<Log(id={self.id}, tipo={self.tipo}, pergunta={self.pergunta}, criado_em={self.criado_em})>"
