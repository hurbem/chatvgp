from sqlalchemy.orm import Session
from anthropic import Anthropic
from app.config import settings
from app.models import Prestador, Categoria, Condominio, Feedback
from app.services.ranking_service import calcular_stats_prestador
import json
import logging
import sys

logger = logging.getLogger(__name__)

try:
    client = Anthropic(api_key=settings.CLAUDE_API_KEY)
    logger.warning(f"✅ Anthropic client inicializado")
except Exception as e:
    logger.error(f"❌ Erro ao inicializar Anthropic: {e}")
    client = None

def extrair_categoria_e_condominio(pergunta: str, db: Session) -> tuple:
    """
    Extrai categoria e condomínio da pergunta usando keyword matching.
    Retorna (categoria_id, condominio_id).
    """
    categorias = db.query(Categoria).all()
    condominios = db.query(Condominio).all()

    pergunta_lower = pergunta.lower()

    # Keyword matching para categorias
    categoria_id = None
    for cat in categorias:
        keywords = cat.nome.lower().split()
        if any(kw in pergunta_lower for kw in keywords):
            categoria_id = cat.id
            logger.warning(f"[EXTRACT] ✅ Categoria encontrada: {cat.nome} (ID: {cat.id})")
            sys.stdout.flush()
            break

    # Keyword matching para condomínios
    condominio_id = None
    for cond in condominios:
        keywords = cond.nome.lower().split() + cond.cidade.lower().split()
        if any(kw in pergunta_lower for kw in keywords):
            condominio_id = cond.id
            logger.warning(f"[EXTRACT] ✅ Condomínio encontrado: {cond.nome} (ID: {cond.id})")
            sys.stdout.flush()
            break

    # Se não encontrou categoria, retorna a primeira
    if not categoria_id and categorias:
        categoria_id = categorias[0].id
        logger.warning(f"[EXTRACT] ⚠️ Categoria não identificada, usando padrão: {categorias[0].nome}")
        sys.stdout.flush()

    # Se não encontrou condomínio, retorna o primeiro
    if not condominio_id and condominios:
        condominio_id = condominios[0].id
        logger.warning(f"[EXTRACT] ⚠️ Condomínio não identificado, usando padrão: {condominios[0].nome}")
        sys.stdout.flush()

    return categoria_id, condominio_id

def buscar_prestadores(
    db: Session, categoria_id: int, condominio_id: int = None, limit: int = 5
) -> list:
    """
    Busca prestadores por categoria e condomínio, ordenados por score.
    """
    query = db.query(Prestador).filter(
        Prestador.categoria_id == categoria_id,
        Prestador.status == "ativo",
    )

    prestadores = query.all()

    # Calcular scores e ordenar
    prestadores_com_score = []
    for p in prestadores:
        # Se condominio_id foi especificado, filtra
        if condominio_id and condominio_id not in p.condominio_ids:
            continue

        stats = calcular_stats_prestador(db, p.id, condominio_id or p.condominio_ids[0])

        prestadores_com_score.append({
            "id": p.id,
            "nome": p.nome,
            "whatsapp": p.whatsapp,
            "link_whatsapp": gerar_link_whatsapp(p.whatsapp),
            "score_final": stats.score_final,
            "feedback_count": stats.total_feedbacks,
            "qualidade_media": stats.qualidade_media,
            "material_acertou_pct": stats.material_acertou_pct,
            "prazo_cumprido_pct": stats.prazo_cumprido_pct,
            "custo_mantido_pct": stats.custo_mantido_pct,
        })

    # Ordenar por score e limitar
    prestadores_com_score.sort(key=lambda x: x["score_final"], reverse=True)
    return prestadores_com_score[:limit]

def gerar_link_whatsapp(whatsapp: str) -> str:
    """
    Gera link de WhatsApp com mensagem padrão.
    """
    mensagem = "Olá encontrei sua recomendação no chatVGP, estou precisando falar contigo"
    # Remove caracteres especiais do whatsapp
    whatsapp_limpo = "".join(filter(str.isdigit, whatsapp))
    return f"https://wa.me/{whatsapp_limpo}?text={mensagem.replace(' ', '%20')}"
