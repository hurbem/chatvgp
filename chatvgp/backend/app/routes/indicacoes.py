from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Indicacao, Condominio, Prestador
from app.schemas.indicacao import IndicacaoCreate, IndicacaoResponse

router = APIRouter(prefix="/api/indicacoes", tags=["indicacoes"])

@router.post("", status_code=status.HTTP_201_CREATED)
def criar_indicacao(
    indicacao: IndicacaoCreate,
    prestador_id: int = None,
    db: Session = Depends(get_db),
):
    """
    Criar nova indicação.
    Se prestador_id for fornecido, associa o prestador à indicação.
    """
    # Validar condomínio existe
    condominio = db.query(Condominio).filter(Condominio.id == indicacao.condominio_id).first()
    if not condominio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Condomínio não existe",
        )

    # Se prestador_id foi fornecido, validar e associar
    if prestador_id:
        prestador = db.query(Prestador).filter(Prestador.id == prestador_id).first()
        if not prestador:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prestador não encontrado",
            )
        # Atualizar prestador com a indicação
        prestador.indicador_id = None  # Será preenchido depois

    nova_indicacao = Indicacao(**indicacao.dict())
    db.add(nova_indicacao)
    db.commit()
    db.refresh(nova_indicacao)

    # Se prestador_id foi fornecido, atualizar o prestador
    if prestador_id:
        prestador.indicador_id = nova_indicacao.id
        db.commit()
        db.refresh(prestador)

    return {
        "id": nova_indicacao.id,
        "condominio_id": nova_indicacao.condominio_id,
        "nome_morador": nova_indicacao.nome_morador,
        "whatsapp_morador": nova_indicacao.whatsapp_morador,
        "criado_em": nova_indicacao.criado_em.isoformat() if nova_indicacao.criado_em else None,
    }

@router.get("")
def listar_indicacoes(
    condominio_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Listar indicações com filtro opcional por condomínio.
    """
    query = db.query(Indicacao)

    if condominio_id:
        query = query.filter(Indicacao.condominio_id == condominio_id)

    indicacoes = query.offset(skip).limit(limit).all()

    return [
        {
            "id": ind.id,
            "condominio_id": ind.condominio_id,
            "nome_morador": ind.nome_morador,
            "whatsapp_morador": ind.whatsapp_morador,
            "criado_em": ind.criado_em.isoformat() if ind.criado_em else None,
        }
        for ind in indicacoes
    ]

@router.get("/{indicacao_id}")
def obter_indicacao(
    indicacao_id: int,
    db: Session = Depends(get_db),
):
    """
    Obter detalhes de uma indicação específica.
    """
    indicacao = db.query(Indicacao).filter(Indicacao.id == indicacao_id).first()

    if not indicacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Indicação não encontrada",
        )

    # Buscar prestadores que foram indicados por essa indicação
    prestadores = db.query(Prestador).filter(Prestador.indicador_id == indicacao_id).all()

    return {
        "id": indicacao.id,
        "condominio_id": indicacao.condominio_id,
        "nome_morador": indicacao.nome_morador,
        "whatsapp_morador": indicacao.whatsapp_morador,
        "criado_em": indicacao.criado_em.isoformat() if indicacao.criado_em else None,
        "prestadores_indicados": [
            {
                "id": p.id,
                "nome": p.nome,
                "categoria_id": p.categoria_id,
            }
            for p in prestadores
        ],
    }

@router.delete("/{indicacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_indicacao(
    indicacao_id: int,
    db: Session = Depends(get_db),
):
    """
    Deletar uma indicação.
    Desassocia qualquer prestador vinculado.
    """
    indicacao = db.query(Indicacao).filter(Indicacao.id == indicacao_id).first()

    if not indicacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Indicação não encontrada",
        )

    # Desassociar prestadores
    prestadores = db.query(Prestador).filter(Prestador.indicador_id == indicacao_id).all()
    for p in prestadores:
        p.indicador_id = None

    db.delete(indicacao)
    db.commit()

    return None
