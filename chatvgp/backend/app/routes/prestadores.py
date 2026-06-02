from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Prestador, Categoria
from app.schemas.prestador import (
    PrestadorCreate,
    PrestadorUpdate,
    PrestadorResponse,
    PrestadorComScore,
)
from app.services.ranking_service import calcular_stats_prestador
from app.utils.security import verify_token

router = APIRouter(prefix="/api/prestadores", tags=["prestadores"])

def verificar_admin(authorization: str = None) -> bool:
    """
    Middleware simples: valida se tem token válido.
    Para MVP, aceita qualquer token não-vazio.
    Em produção: usar JWT properly.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação necessário",
        )
    return True

@router.get("", response_model=List[PrestadorComScore])
def listar_prestadores(
    categoria_id: int = None,
    condominio_id: int = None,
    status_filter: str = "ativo",
    db: Session = Depends(get_db),
):
    """
    Listar prestadores com scores calculados.
    Público (sem autenticação).
    """
    query = db.query(Prestador)

    if categoria_id:
        query = query.filter(Prestador.categoria_id == categoria_id)

    if status_filter:
        query = query.filter(Prestador.status == status_filter)

    prestadores = query.all()

    result = []
    for p in prestadores:
        # Calcular score para cada condomínio onde trabalha
        if p.condominio_ids:
            condominio_id = p.condominio_ids[0]
            stats = calcular_stats_prestador(db, p.id, condominio_id)
        else:
            stats = None

        result.append(
            PrestadorComScore(
                id=p.id,
                nome=p.nome,
                whatsapp=p.whatsapp,
                categoria_id=p.categoria_id,
                condominio_ids=p.condominio_ids,
                status=p.status,
                notas=p.notas,
                criado_em=p.criado_em,
                categoria=p.categoria,
                score_final=stats.score_final if stats else 0,
                feedback_count=stats.total_feedbacks if stats else 0,
                qualidade_media=stats.qualidade_media if stats else None,
                material_acertou_pct=stats.material_acertou_pct if stats else None,
                prazo_cumprido_pct=stats.prazo_cumprido_pct if stats else None,
                custo_mantido_pct=stats.custo_mantido_pct if stats else None,
            )
        )

    return result

@router.get("/{prestador_id}", response_model=PrestadorComScore)
def obter_prestador(prestador_id: int, db: Session = Depends(get_db)):
    """
    Obter detalhes de um prestador com score.
    Público.
    """
    prestador = db.query(Prestador).filter(Prestador.id == prestador_id).first()

    if not prestador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prestador não encontrado",
        )

    if prestador.condominio_ids:
        stats = calcular_stats_prestador(db, prestador.id, prestador.condominio_ids[0])
    else:
        stats = None

    return PrestadorComScore(
        id=prestador.id,
        nome=prestador.nome,
        whatsapp=prestador.whatsapp,
        categoria_id=prestador.categoria_id,
        condominio_ids=prestador.condominio_ids,
        status=prestador.status,
        notas=prestador.notas,
        criado_em=prestador.criado_em,
        categoria=prestador.categoria,
        score_final=stats.score_final if stats else 0,
        feedback_count=stats.total_feedbacks if stats else 0,
        qualidade_media=stats.qualidade_media if stats else None,
        material_acertou_pct=stats.material_acertou_pct if stats else None,
        prazo_cumprido_pct=stats.prazo_cumprido_pct if stats else None,
        custo_mantido_pct=stats.custo_mantido_pct if stats else None,
    )

@router.post("", response_model=PrestadorResponse, status_code=status.HTTP_201_CREATED)
def criar_prestador(
    prestador: PrestadorCreate,
    db: Session = Depends(get_db),
    authorization: str = None,
):
    """
    Criar novo prestador.
    Admin only (requer header Authorization).
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação necessário",
        )

    # Validar categoria existe
    categoria = db.query(Categoria).filter(Categoria.id == prestador.categoria_id).first()
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Categoria não existe",
        )

    # Validar se já existe com mesmo nome
    existing = db.query(Prestador).filter(Prestador.nome == prestador.nome).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prestador com este nome já existe",
        )

    novo_prestador = Prestador(**prestador.dict())
    db.add(novo_prestador)
    db.commit()
    db.refresh(novo_prestador)

    return novo_prestador

@router.put("/{prestador_id}", response_model=PrestadorResponse)
def atualizar_prestador(
    prestador_id: int,
    prestador_update: PrestadorUpdate,
    db: Session = Depends(get_db),
    authorization: str = None,
):
    """
    Atualizar prestador existente.
    Admin only.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação necessário",
        )

    prestador = db.query(Prestador).filter(Prestador.id == prestador_id).first()

    if not prestador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prestador não encontrado",
        )

    # Validar categoria se estiver sendo alterada
    if prestador_update.categoria_id:
        categoria = db.query(Categoria).filter(Categoria.id == prestador_update.categoria_id).first()
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Categoria não existe",
            )

    # Atualizar apenas campos não-None
    dados_atualizacao = prestador_update.dict(exclude_unset=True)
    for campo, valor in dados_atualizacao.items():
        if valor is not None:
            setattr(prestador, campo, valor)

    db.commit()
    db.refresh(prestador)

    return prestador

@router.delete("/{prestador_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_prestador(
    prestador_id: int,
    db: Session = Depends(get_db),
    authorization: str = None,
):
    """
    Deletar prestador.
    Admin only.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação necessário",
        )

    prestador = db.query(Prestador).filter(Prestador.id == prestador_id).first()

    if not prestador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prestador não encontrado",
        )

    db.delete(prestador)
    db.commit()

    return None
