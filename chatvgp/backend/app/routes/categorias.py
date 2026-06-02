from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.database import get_db
from app.models import Categoria

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

@router.get("", response_model=List[CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db)):
    """Listar todas as categorias (público)."""
    return db.query(Categoria).all()

@router.get("/{categoria_id}", response_model=CategoriaResponse)
def obter_categoria(categoria_id: int, db: Session = Depends(get_db)):
    """Obter detalhes de uma categoria."""
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return categoria

@router.post("", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
def criar_categoria(
    categoria: CategoriaCreate,
    db: Session = Depends(get_db),
    authorization: str = None,
):
    """Criar nova categoria (admin only)."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Autenticação necessária")

    existing = db.query(Categoria).filter(Categoria.nome == categoria.nome).first()
    if existing:
        raise HTTPException(status_code=400, detail="Categoria já existe")

    nova_categoria = Categoria(**categoria.dict())
    db.add(nova_categoria)
    db.commit()
    db.refresh(nova_categoria)
    return nova_categoria

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
