from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from app.database import get_db
from app.models import Feedback, Prestador, Condominio, Categoria
from app.schemas.feedback import (
    FeedbackCreate,
    FeedbackResponse,
    FeedbackStats,
)
from app.services.ranking_service import calcular_stats_prestador

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

@router.get("")
def listar_feedbacks(
    prestador_id: int = None,
    condominio_id: int = None,
    categoria_id: int = None,
    seu_feedback: bool = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Listar feedbacks com filtros.
    Público (sem autenticação).
    """
    query = db.query(Feedback)

    if prestador_id:
        query = query.filter(Feedback.prestador_id == prestador_id)

    if condominio_id:
        query = query.filter(Feedback.condominio_id == condominio_id)

    if categoria_id:
        query = query.filter(Feedback.categoria_id == categoria_id)

    if seu_feedback is not None:
        query = query.filter(Feedback.seu_feedback == seu_feedback)

    # Ordenar por data decrescente
    query = query.order_by(Feedback.data_feedback.desc())

    # Paginação
    total = query.count()
    feedbacks = query.offset(skip).limit(limit).all()

    return feedbacks

@router.get("/prestador/{prestador_id}")
def listar_feedbacks_prestador(
    prestador_id: int,
    condominio_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Listar feedbacks de um prestador específico.
    Público.
    """
    prestador = db.query(Prestador).filter(Prestador.id == prestador_id).first()
    if not prestador:
        raise HTTPException(status_code=404, detail="Prestador não encontrado")

    query = db.query(Feedback).filter(Feedback.prestador_id == prestador_id)

    if condominio_id:
        query = query.filter(Feedback.condominio_id == condominio_id)

    query = query.order_by(Feedback.data_feedback.desc())

    return query.offset(skip).limit(limit).all()

@router.get("/stats/{prestador_id}")
def obter_stats_prestador(
    prestador_id: int,
    condominio_id: int = None,
    db: Session = Depends(get_db),
):
    """
    Obter estatísticas agregadas de um prestador.
    Se condominio_id não for especificado, usa o primeiro que o prestador trabalha.
    Público.
    """
    prestador = db.query(Prestador).filter(Prestador.id == prestador_id).first()
    if not prestador:
        raise HTTPException(status_code=404, detail="Prestador não encontrado")

    # Se condominio_id não foi especificado, usar o primeiro do prestador
    if not condominio_id:
        if prestador.condominio_ids:
            condominio_id = prestador.condominio_ids[0]
        else:
            raise HTTPException(
                status_code=400,
                detail="Prestador não tem condomínios associados. Especifique condominio_id.",
            )

    stats = calcular_stats_prestador(db, prestador_id, condominio_id)
    return stats

@router.post("", status_code=status.HTTP_201_CREATED)
def criar_feedback(
    feedback: FeedbackCreate,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Criar novo feedback.
    Admin only (requer header Authorization: Bearer <token>).
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação necessário",
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Scheme inválido. Use: Authorization: Bearer <token>",
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de Authorization inválido",
        )

    from app.utils.security import verify_token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

    # Validar se prestador existe
    prestador = db.query(Prestador).filter(Prestador.id == feedback.prestador_id).first()
    if not prestador:
        raise HTTPException(status_code=400, detail="Prestador não existe")

    # Validar se condominio existe
    condominio = db.query(Condominio).filter(Condominio.id == feedback.condominio_id).first()
    if not condominio:
        raise HTTPException(status_code=400, detail="Condomínio não existe")

    # Validar se categoria existe
    categoria = db.query(Categoria).filter(Categoria.id == feedback.categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=400, detail="Categoria não existe")

    # Validar qualidade (1-5)
    if feedback.qualidade < 1 or feedback.qualidade > 5:
        raise HTTPException(status_code=400, detail="Qualidade deve ser entre 1 e 5")

    # Validar material_estimativa
    valores_validos = [
        "Acertou",
        "Subestimou 10-25%",
        "Subestimou 25-50%",
        "Subestimou >50%",
    ]
    if feedback.material_estimativa not in valores_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Material estimativa inválido. Valores válidos: {valores_validos}",
        )

    novo_feedback = Feedback(**feedback.dict())
    db.add(novo_feedback)
    db.commit()
    db.refresh(novo_feedback)

    return novo_feedback

@router.get("/{feedback_id}")
def obter_feedback(feedback_id: int, db: Session = Depends(get_db)):
    """Obter detalhes de um feedback (público)."""
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()

    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback não encontrado")

    return feedback

@router.put("/{feedback_id}")
def atualizar_feedback(
    feedback_id: int,
    feedback_update: FeedbackCreate,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Atualizar feedback existente.
    Admin only (requer token).
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação necessário",
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Scheme inválido. Use: Authorization: Bearer <token>",
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de Authorization inválido",
        )

    from app.utils.security import verify_token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()

    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback não encontrado")

    # Validar referências estrangeiras
    prestador = db.query(Prestador).filter(Prestador.id == feedback_update.prestador_id).first()
    if not prestador:
        raise HTTPException(status_code=400, detail="Prestador não existe")

    condominio = db.query(Condominio).filter(Condominio.id == feedback_update.condominio_id).first()
    if not condominio:
        raise HTTPException(status_code=400, detail="Condomínio não existe")

    categoria = db.query(Categoria).filter(Categoria.id == feedback_update.categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=400, detail="Categoria não existe")

    # Validar qualidade
    if feedback_update.qualidade < 1 or feedback_update.qualidade > 5:
        raise HTTPException(status_code=400, detail="Qualidade deve ser entre 1 e 5")

    # Validar material_estimativa
    valores_validos = [
        "Acertou",
        "Subestimou 10-25%",
        "Subestimou 25-50%",
        "Subestimou >50%",
    ]
    if feedback_update.material_estimativa not in valores_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Material estimativa inválido. Valores válidos: {valores_validos}",
        )

    # Atualizar campos
    for campo, valor in feedback_update.dict().items():
        setattr(feedback, campo, valor)

    db.commit()
    db.refresh(feedback)

    return feedback

@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Deletar feedback.
    Admin only (requer token).
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação necessário",
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Scheme inválido. Use: Authorization: Bearer <token>",
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de Authorization inválido",
        )

    from app.utils.security import verify_token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()

    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback não encontrado")

    db.delete(feedback)
    db.commit()

    return None

@router.get("/ranking/por-condominio/{condominio_id}")
def ranking_por_condominio(
    condominio_id: int,
    categoria_id: int = None,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """
    Obter ranking de prestadores por condomínio.
    Público.
    """
    condominio = db.query(Condominio).filter(Condominio.id == condominio_id).first()
    if not condominio:
        raise HTTPException(status_code=404, detail="Condomínio não encontrado")

    # Buscar prestadores que trabalham neste condomínio
    query = db.query(Prestador).filter(
        Prestador.status == "ativo",
    )

    if categoria_id:
        query = query.filter(Prestador.categoria_id == categoria_id)

    prestadores = query.all()

    # Filtrar por condomínio
    prestadores = [p for p in prestadores if condominio_id in p.condominio_ids]

    # Calcular scores
    ranking = []
    for p in prestadores:
        stats = calcular_stats_prestador(db, p.id, condominio_id)

        ranking.append({
            "id": p.id,
            "nome": p.nome,
            "whatsapp": p.whatsapp,
            "categoria": p.categoria.nome,
            "score_final": stats.score_final,
            "posicao": 0,  # Será preenchido após ordenação
            "qualidade_media": stats.qualidade_media,
            "material_acertou_pct": stats.material_acertou_pct,
            "prazo_cumprido_pct": stats.prazo_cumprido_pct,
            "custo_mantido_pct": stats.custo_mantido_pct,
            "feedback_count": stats.total_feedbacks,
        })

    # Ordenar por score
    ranking.sort(key=lambda x: x["score_final"], reverse=True)

    # Adicionar posição
    for idx, item in enumerate(ranking, 1):
        item["posicao"] = idx

    # Limitar
    return ranking[:limit]
