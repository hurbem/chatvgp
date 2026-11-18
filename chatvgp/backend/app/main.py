import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings, CORS_ORIGINS_LIST
from app.database import Base, engine
from app.middleware import SecurityMiddleware
from app import models  # noqa: F401  (registra os models no Base)
from app.routes import chat, prestadores, categorias, auth, logs, aliases

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Cria as tabelas que ainda não existirem (não altera tabelas existentes)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ChatVGP API",
    description="API para ChatVGP - Busca de prestadores de serviço",
    version="0.2.0",
)

# Security Middleware (bloqueio de bots + rate limit)
app.add_middleware(SecurityMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(prestadores.router)
app.include_router(categorias.router)
app.include_router(logs.router)
app.include_router(aliases.router)


@app.get("/health")
def health():
    return {"status": "ok", "version": app.version, "environment": settings.ENVIRONMENT}


@app.get("/")
def root():
    return {"message": "ChatVGP API - Use /docs para documentação"}
