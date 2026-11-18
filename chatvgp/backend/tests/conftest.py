import os
import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Garante que os testes nunca rodem com configuração de produção
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "chave-de-teste"
os.environ["ADMIN_PASSWORD"] = "senha-de-teste-admin"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import Base, get_db  # noqa: E402
from app.models import Categoria, Prestador  # noqa: E402


@pytest.fixture
def db():
    """Banco SQLite em memória, novo para cada teste."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    """Cliente HTTP da API usando o banco de teste."""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.middleware import security_middleware

    security_middleware.rate_limit_store.clear()
    security_middleware.login_attempts_store.clear()

    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app, headers={"User-Agent": "Mozilla/5.0 (testes)"}) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_headers(client):
    resp = client.post("/api/auth/login", json={"senha": "senha-de-teste-admin"})
    assert resp.status_code == 200
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def criar_categoria(db, nome, aliases=None, ordem=999):
    cat = Categoria(nome=nome, aliases=aliases, ordem=ordem)
    db.add(cat)
    db.commit()
    return cat


def criar_prestador(db, nome, whatsapp, categorias, status="ativo", **extra):
    p = Prestador(nome=nome, whatsapp=whatsapp, status=status, **extra)
    p.categorias = list(categorias)
    db.add(p)
    db.commit()
    return p
