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

@router.get("")
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
        # Calcular score agregado de todos os feedbacks
        # Se condominio_id foi filtrado, usa esse; senão calcula agregado
        from app.models import Feedback

        if condominio_id:
            # Se foi especificado um condomínio, calcula score para ele
            stats = calcular_stats_prestador(db, p.id, condominio_id)
        else:
            # Senão, usa agregado de todos os feedbacks
            feedbacks = db.query(Feedback).filter(Feedback.prestador_id == p.id).all()
            if feedbacks:
                # Calcula agregado simples
                total = len(feedbacks)
                qualidade_media = sum(f.qualidade for f in feedbacks) / total if feedbacks else 0
                material_acertou = sum(1 for f in feedbacks if f.material_estimativa == "Acertou") / total if feedbacks else 0
                prazo_cumprido = sum(1 for f in feedbacks if f.prazo_manteve) / total if feedbacks else 0
                custo_mantido = sum(1 for f in feedbacks if f.custo_manteve) / total if feedbacks else 0

                score_final = (material_acertou * 2) + (prazo_cumprido * 1.5) + (custo_mantido * 1.5) + qualidade_media

                class Stats:
                    pass
                stats = Stats()
                stats.score_final = round(score_final, 2)
                stats.total_feedbacks = total
                stats.qualidade_media = round(qualidade_media, 1)
                stats.material_acertou_pct = round(material_acertou, 2)
                stats.prazo_cumprido_pct = round(prazo_cumprido, 2)
                stats.custo_mantido_pct = round(custo_mantido, 2)
            else:
                stats = None

        result.append({
            "id": p.id,
            "nome": p.nome,
            "whatsapp": p.whatsapp,
            "categoria_id": p.categoria_id,
            "status": p.status,
            "notas": p.notas,
            "criado_em": p.criado_em.isoformat() if p.criado_em else None,
            "categoria": {"id": p.categoria.id, "nome": p.categoria.nome} if p.categoria else None,
            "score_final": stats.score_final if stats else 0,
            "feedback_count": stats.total_feedbacks if stats else 0,
            "qualidade_media": stats.qualidade_media if stats else None,
            "material_acertou_pct": stats.material_acertou_pct if stats else None,
            "prazo_cumprido_pct": stats.prazo_cumprido_pct if stats else None,
            "custo_mantido_pct": stats.custo_mantido_pct if stats else None,
        })

    return result

@router.get("/{prestador_id}")
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

    from app.models import Feedback

    # Calcular score agregado
    feedbacks = db.query(Feedback).filter(Feedback.prestador_id == prestador.id).all()
    if feedbacks:
        total = len(feedbacks)
        qualidade_media = sum(f.qualidade for f in feedbacks) / total
        material_acertou = sum(1 for f in feedbacks if f.material_estimativa == "Acertou") / total
        prazo_cumprido = sum(1 for f in feedbacks if f.prazo_manteve) / total
        custo_mantido = sum(1 for f in feedbacks if f.custo_manteve) / total

        score_final = (material_acertou * 2) + (prazo_cumprido * 1.5) + (custo_mantido * 1.5) + qualidade_media

        class Stats:
            pass
        stats = Stats()
        stats.score_final = round(score_final, 2)
        stats.total_feedbacks = total
        stats.qualidade_media = round(qualidade_media, 1)
        stats.material_acertou_pct = round(material_acertou, 2)
        stats.prazo_cumprido_pct = round(prazo_cumprido, 2)
        stats.custo_mantido_pct = round(custo_mantido, 2)
    else:
        stats = None

    return {
        "id": prestador.id,
        "nome": prestador.nome,
        "whatsapp": prestador.whatsapp,
        "categoria_id": prestador.categoria_id,
        "status": prestador.status,
        "notas": prestador.notas,
        "criado_em": prestador.criado_em.isoformat() if prestador.criado_em else None,
        "categoria": {"id": prestador.categoria.id, "nome": prestador.categoria.nome} if prestador.categoria else None,
        "score_final": stats.score_final if stats else 0,
        "feedback_count": stats.total_feedbacks if stats else 0,
        "qualidade_media": stats.qualidade_media if stats else None,
        "material_acertou_pct": stats.material_acertou_pct if stats else None,
        "prazo_cumprido_pct": stats.prazo_cumprido_pct if stats else None,
        "custo_mantido_pct": stats.custo_mantido_pct if stats else None,
    }

@router.post("", status_code=status.HTTP_201_CREATED)
def criar_prestador(
    prestador: PrestadorCreate,
    db: Session = Depends(get_db),
    authorization: str = None,
):
    """
    Criar novo prestador.
    Admin only (requer header Authorization: Bearer <token>).
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação necessário",
        )

    # Extrair token do header "Authorization: Bearer <token>"
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

    # Verificar token
    from app.utils.security import verify_token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
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

@router.put("/{prestador_id}")
def atualizar_prestador(
    prestador_id: int,
    prestador_update: PrestadorUpdate,
    db: Session = Depends(get_db),
    authorization: str = None,
):
    """
    Atualizar prestador existente.
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

    return {
        "id": prestador.id,
        "nome": prestador.nome,
        "whatsapp": prestador.whatsapp,
        "categoria_id": prestador.categoria_id,
        "condominio_ids": prestador.condominio_ids,
        "status": prestador.status,
        "notas": prestador.notas,
        "criado_em": prestador.criado_em.isoformat() if prestador.criado_em else None,
    }

@router.delete("/{prestador_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_prestador(
    prestador_id: int,
    db: Session = Depends(get_db),
    authorization: str = None,
):
    """
    Deletar prestador.
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

    prestador = db.query(Prestador).filter(Prestador.id == prestador_id).first()

    if not prestador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prestador não encontrado",
        )

    db.delete(prestador)
    db.commit()

    return None
