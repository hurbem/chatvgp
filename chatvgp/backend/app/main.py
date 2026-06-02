from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings, CORS_ORIGINS_LIST
from app.database import Base, engine

# Criar tabelas
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas/verificadas com sucesso")
except Exception as e:
    print(f"⚠️ Aviso ao criar tabelas: {e}")

try:
    from app.routes import chat, prestadores, categorias, condominios, feedback
    routes_available = True
except Exception as e:
    print(f"Warning: Could not load routes: {e}")
    routes_available = False

app = FastAPI(
    title="ChatVGP API",
    description="API para ChatVGP - Busca de prestadores por IA",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas se disponíveis
if routes_available:
    app.include_router(chat.router)
    app.include_router(prestadores.router)
    app.include_router(categorias.router)
    app.include_router(condominios.router)
    app.include_router(feedback.router)

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}

@app.get("/")
def root():
    return {"message": "ChatVGP API v0.1.0 - Use /docs para documentação"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
