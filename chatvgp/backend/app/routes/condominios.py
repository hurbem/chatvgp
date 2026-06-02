from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app.models import Condominio

router = APIRouter(prefix="/api/condominios", tags=["condominios"])

class CondominioCreate(BaseModel):
    nome: str
    cidade: str

class CondominioResponse(BaseModel):
    id: int
    nome: str
    cidade: str
    criado_em: datetime

    class Config:
        orm_mode = True

@router.get("", response_model=List[CondominioResponse])
def listar_condominios(cidade: str = None, db: Session = Depends(get_db)):
    """Listar condomínios (público)."""
    query = db.query(Condominio)
    if cidade:
        query = query.filter(Condominio.cidade == cidade)
    return query.all()

@router.get("/{condominio_id}", response_model=CondominioResponse)
def obter_condominio(condominio_id: int, db: Session = Depends(get_db)):
    """Obter detalhes de um condomínio."""
    condominio = db.query(Condominio).filter(Condominio.id == condominio_id).first()
    if not condominio:
        raise HTTPException(status_code=404, detail="Condomínio não encontrado")
    return condominio

@router.post("", response_model=CondominioResponse, status_code=status.HTTP_201_CREATED)
def criar_condominio(
    condominio: CondominioCreate,
    db: Session = Depends(get_db),
    authorization: str = None,
):
    """Criar novo condomínio (admin only)."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Autenticação necessária")

    novo_condominio = Condominio(**condominio.dict())
    db.add(novo_condominio)
    db.commit()
    db.refresh(novo_condominio)
    return novo_condominio

@router.put("/{condominio_id}", response_model=CondominioResponse)
def atualizar_condominio(
    condominio_id: int,
    condominio_update: CondominioCreate,
    db: Session = Depends(get_db),
    authorization: str = None,
):
    """Atualizar condomínio (admin only)."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Autenticação necessária")

    condominio = db.query(Condominio).filter(Condominio.id == condominio_id).first()
    if not condominio:
        raise HTTPException(status_code=404, detail="Condomínio não encontrado")

    condominio.nome = condominio_update.nome
    condominio.cidade = condominio_update.cidade
    db.commit()
    db.refresh(condominio)
    return condominio

@router.delete("/{condominio_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_condominio(
    condominio_id: int,
    db: Session = Depends(get_db),
    authorization: str = None,
):
    """Deletar condomínio (admin only)."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Autenticação necessária")

    condominio = db.query(Condominio).filter(Condominio.id == condominio_id).first()
    if not condominio:
        raise HTTPException(status_code=404, detail="Condomínio não encontrado")

    db.delete(condominio)
    db.commit()
