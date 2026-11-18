from pydantic import BaseSettings
import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env (se existir) para o ambiente do processo
load_dotenv()

DEFAULT_SECRET_KEY = "dev-secret-key"


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/chatvgp")
    # Chave usada APENAS para assinar os tokens JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY)
    # Senha de login do admin (separada da chave de assinatura)
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CLAUDE_API_KEY: str = os.getenv("CLAUDE_API_KEY", "")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    class Config:
        case_sensitive = True


# Parse CORS_ORIGINS from env (comma-separated string)
cors_env = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000,http://localhost:5173,http://127.0.0.1:3000")
CORS_ORIGINS_LIST = [url.strip() for url in cors_env.split(",") if url.strip()]

settings = Settings()

# Em produção, não sobe com chave padrão ou sem senha de admin
if settings.ENVIRONMENT == "production":
    problemas = []
    if not settings.SECRET_KEY or settings.SECRET_KEY == DEFAULT_SECRET_KEY:
        problemas.append("SECRET_KEY não configurada (ou com valor padrão)")
    if len(settings.ADMIN_PASSWORD) < 16:
        problemas.append("ADMIN_PASSWORD não configurada (ou com menos de 16 caracteres)")
    if settings.ADMIN_PASSWORD and settings.ADMIN_PASSWORD == settings.SECRET_KEY:
        problemas.append("ADMIN_PASSWORD deve ser diferente de SECRET_KEY")
    if problemas:
        raise RuntimeError("Configuração insegura em produção: " + "; ".join(problemas))
