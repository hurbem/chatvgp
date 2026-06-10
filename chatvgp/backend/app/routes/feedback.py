from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app.models import Feedback, Prestador, Condominio, Categoria, Log, FeedbackLink
from app.schemas.feedback import (
    FeedbackCreate,
    FeedbackResponse,
    FeedbackStats,
)
from app.services.ranking_service import calcular_stats_prestador

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

# Schemas para indicação
class IndicacaoCreate(BaseModel):
    condominio_id: int
    nome_morador: str
    whatsapp_morador: str
    prestador_id: Optional[int] = None
    prestador_nome: str
    categoria_id: int
    whatsapp_prestador: str
    instagram: Optional[str] = None
    site: Optional[str] = None
    notas: Optional[str] = None

# Schemas para links de feedback
class FeedbackLinkResponse(BaseModel):
    id: int
    prestador_id: int
    token: str
    expirado_em: str
    usado: bool
    criado_em: str
    link_completo: str

class FeedbackViaLink(BaseModel):
    condominio_id: int
    qualidade: int  # 1-5
    material_estimativa: str
    prazo_manteve: bool
    custo_manteve: bool
    seu_feedback: bool = True
    notas: Optional[str] = None

@router.post("/indicacoes", status_code=status.HTTP_201_CREATED)
def registrar_indicacao(
    indicacao: IndicacaoCreate,
    db: Session = Depends(get_db),
):
    """
    Registra uma indicação de profissional.
    Público (sem autenticação).
    """
    try:
        # Registrar log da indicação
        novo_log = Log(
            tipo="INDICACAO_PROFISSIONAL",
            pergunta=f"Indicação de {indicacao.prestador_nome}",
            categoria_encontrada=None,
            condominio_encontrado=None,
            mensagem=f"Indicador: {indicacao.nome_morador} | Condominio: {indicacao.condominio_id} | Prestador: {indicacao.prestador_nome} ({indicacao.whatsapp_prestador})"
        )
        db.add(novo_log)
        db.commit()

        return {
            "success": True,
            "message": "Indicação registrada com sucesso",
            "log_id": novo_log.id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao registrar indicação: {str(e)}"
        )

@router.post("/gerar-link/{prestador_id}", status_code=status.HTTP_201_CREATED)
def gerar_link_feedback(
    prestador_id: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Gera um link personalizado de feedback para um prestador.
    Admin only (requer token).
    Link expira em 7 dias e pode ser usado apenas uma vez.
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

    # Verificar se prestador existe
    prestador = db.query(Prestador).filter(Prestador.id == prestador_id).first()
    if not prestador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prestador não encontrado",
        )

    # Gerar novo link de feedback
    novo_link = FeedbackLink(
        prestador_id=prestador_id,
        token=FeedbackLink.gerar_token(),
        expirado_em=FeedbackLink.gerar_link_expiracao(),
    )
    db.add(novo_link)
    db.commit()
    db.refresh(novo_link)

    link_completo = f"https://api.chatvgp.com/api/feedback/enviar/{novo_link.token}"

    return {
        "id": novo_link.id,
        "prestador_id": novo_link.prestador_id,
        "token": novo_link.token,
        "expirado_em": novo_link.expirado_em.isoformat(),
        "usado": novo_link.usado,
        "criado_em": novo_link.criado_em.isoformat(),
        "link_completo": link_completo,
        "mensagem": "Link gerado com sucesso. Validade: 7 dias. Uso único.",
    }

@router.get("/enviar/{token}")
def obter_formulario_feedback(
    token: str,
    db: Session = Depends(get_db),
):
    """
    Obtém o formulário de feedback usando um link personalizado.
    Público (sem autenticação).
    Valida o token antes de exibir o formulário.
    """
    # Buscar o link
    feedback_link = db.query(FeedbackLink).filter(FeedbackLink.token == token).first()

    if not feedback_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link de feedback inválido ou não encontrado",
        )

    # Validar se o link é válido
    if not feedback_link.esta_valido():
        if feedback_link.usado:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Este link já foi utilizado uma vez",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Este link expirou",
            )

    # Buscar dados do prestador
    prestador = db.query(Prestador).filter(Prestador.id == feedback_link.prestador_id).first()
    if not prestador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prestador não encontrado",
        )

    # Buscar condominios para o dropdown
    condominios = db.query(Condominio).all()

    return {
        "success": True,
        "token": token,
        "prestador": {
            "id": prestador.id,
            "nome": prestador.nome,
            "categoria": prestador.categoria.nome,
        },
        "condominios": [
            {"id": c.id, "nome": f"{c.nome} - {c.cidade}"} for c in condominios
        ],
        "form_fields": {
            "condominio_id": {"type": "select", "label": "Seu condomínio", "required": True},
            "qualidade": {"type": "number", "label": "Qualidade do trabalho (1-5)", "min": 1, "max": 5, "required": True},
            "material_estimativa": {"type": "select", "label": "Material/Estimativa", "required": True, "options": ["Acertou", "Subestimou 10-25%", "Subestimou 25-50%", "Subestimou >50%"]},
            "prazo_manteve": {"type": "boolean", "label": "Cumpriu o prazo?", "required": True},
            "custo_manteve": {"type": "boolean", "label": "Manteve o custo?", "required": True},
            "notas": {"type": "textarea", "label": "Observações (opcional)", "required": False},
        }
    }

@router.post("/enviar/{token}", status_code=status.HTTP_201_CREATED)
def enviar_feedback_via_link(
    token: str,
    feedback: FeedbackViaLink,
    db: Session = Depends(get_db),
):
    """
    Submete um feedback usando um link personalizado.
    Público (sem autenticação).
    Valida o token e marca como usado após submissão.
    """
    # Buscar o link
    feedback_link = db.query(FeedbackLink).filter(FeedbackLink.token == token).first()

    if not feedback_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link de feedback inválido ou não encontrado",
        )

    # Validar se o link é válido
    if not feedback_link.esta_valido():
        if feedback_link.usado:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Este link já foi utilizado uma vez",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Este link expirou",
            )

    # Validar feedback
    if feedback.qualidade < 1 or feedback.qualidade > 5:
        raise HTTPException(
            status_code=400,
            detail="Qualidade deve ser entre 1 e 5",
        )

    valores_validos = [
        "Acertou",
        "Subestimou 10-25%",
        "Subestimou 25-50%",
        "Subestimou >50%",
    ]
    if feedback.material_estimativa not in valores_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Material estimativa inválido",
        )

    # Validar condominio
    condominio = db.query(Condominio).filter(Condominio.id == feedback.condominio_id).first()
    if not condominio:
        raise HTTPException(
            status_code=400,
            detail="Condomínio não existe",
        )

    # Criar feedback
    novo_feedback = Feedback(
        prestador_id=feedback_link.prestador_id,
        condominio_id=feedback.condominio_id,
        categoria_id=db.query(Prestador).filter(Prestador.id == feedback_link.prestador_id).first().categoria_id,
        qualidade=feedback.qualidade,
        material_estimativa=feedback.material_estimativa,
        prazo_manteve=feedback.prazo_manteve,
        custo_manteve=feedback.custo_manteve,
        seu_feedback=feedback.seu_feedback,
        notas=feedback.notas,
    )
    db.add(novo_feedback)

    # Marcar link como usado
    feedback_link.usado = True
    feedback_link.usado_em = datetime.utcnow()
    db.add(feedback_link)

    db.commit()
    db.refresh(novo_feedback)

    return {
        "success": True,
        "message": "Feedback enviado com sucesso. Obrigado!",
        "feedback_id": novo_feedback.id,
    }

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
