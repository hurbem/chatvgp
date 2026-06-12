from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from pydantic import BaseModel
from app.database import get_db
from app.models import Categoria
from app.services.categoria_service import gerar_aliases_com_claude

router = APIRouter(prefix="/api/categorias", tags=["categorias"])

class CategoriaCreate(BaseModel):
    nome: str
    descricao: str = None

class CategoriaResponse(BaseModel):
    id: int
    nome: str
    descricao: str = None

    class Config:
        orm_mode = True

@router.get("")
def listar_categorias(db: Session = Depends(get_db)):
    """Listar todas as categorias (público) - ordenadas por 'ordem'."""
    categorias = db.query(Categoria).order_by(text("ordem")).all()
    return [
        {
            "id": c.id,
            "nome": c.nome,
            "descricao": c.descricao,
        }
        for c in categorias
    ]

@router.get("/{categoria_id}")
def obter_categoria(categoria_id: int, db: Session = Depends(get_db)):
    """Obter detalhes de uma categoria."""
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return categoria

@router.post("", status_code=status.HTTP_201_CREATED)
def criar_categoria(
    categoria: CategoriaCreate,
    db: Session = Depends(get_db),
):
    """Criar nova categoria com aliases gerados automaticamente pelo Claude."""

    existing = db.query(Categoria).filter(Categoria.nome == categoria.nome).first()
    if existing:
        raise HTTPException(status_code=400, detail="Categoria já existe")

    # Gerar aliases com Claude API
    print(f"🔄 Gerando aliases para '{categoria.nome}'...")
    aliases = gerar_aliases_com_claude(categoria.nome)

    # Criar categoria com aliases
    nova_categoria = Categoria(
        nome=categoria.nome,
        descricao=categoria.descricao,
        aliases=aliases
    )
    db.add(nova_categoria)
    db.commit()
    db.refresh(nova_categoria)

    return {
        "id": nova_categoria.id,
        "nome": nova_categoria.nome,
        "descricao": nova_categoria.descricao,
        "aliases": nova_categoria.aliases,
        "mensagem": f"✅ Categoria '{nova_categoria.nome}' criada com aliases: {aliases}",
    }

@router.put("/{categoria_id}", response_model=CategoriaResponse)
def atualizar_categoria(
    categoria_id: int,
    categoria_update: CategoriaCreate,
    db: Session = Depends(get_db),
    authorization: str = None,
):
    """Atualizar categoria (admin only)."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Autenticação necessária")

    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    categoria.nome = categoria_update.nome
    categoria.descricao = categoria_update.descricao
    db.commit()
    db.refresh(categoria)
    return categoria

@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    authorization: str = None,
):
    """Deletar categoria (admin only)."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Autenticação necessária")

    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    db.delete(categoria)
    db.commit()
