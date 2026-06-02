from pydantic import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/chatvgp")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CLAUDE_API_KEY: str = os.getenv("CLAUDE_API_KEY", "sk-placeholder")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000", "http://localhost:5173", "https://chatvgp.vercel.app"]

    class Config:
        case_sensitive = True

try:
    settings = Settings()
except Exception as e:
    print(f"Warning: Could not load settings: {e}")
    settings = Settings()
