from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from app.database import Base
from datetime import datetime, timedelta
import secrets

class FeedbackLink(Base):
    """
    Modelo para armazenar links personalizados de feedback.
    Cada prestador pode gerar links para receber feedback dos clientes.
    """
    __tablename__ = "feedback_links"

    id = Column(Integer, primary_key=True, index=True)
    prestador_id = Column(Integer, ForeignKey("prestadores.id"), index=True, nullable=False)
    token = Column(String(128), unique=True, index=True, nullable=False)  # Token único
    expirado_em = Column(DateTime, index=True, nullable=False)  # Data de expiração (7 dias)
    usado = Column(Boolean, default=False, index=True)  # Se já foi usado
    usado_em = Column(DateTime, nullable=True)  # Data/hora que foi usado
    criado_em = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<FeedbackLink(id={self.id}, prestador_id={self.prestador_id}, token={self.token[:10]}..., expirado_em={self.expirado_em}, usado={self.usado})>"

    @staticmethod
    def gerar_token() -> str:
        """Gera um token único e seguro para o link."""
        return secrets.token_urlsafe(32)

    def esta_valido(self) -> bool:
        """Verifica se o link ainda é válido."""
        return not self.usado and datetime.utcnow() < self.expirado_em

    @staticmethod
    def gerar_link_expiracao() -> datetime:
        """Gera a data de expiração (7 dias a partir de agora)."""
        return datetime.utcnow() + timedelta(days=7)
