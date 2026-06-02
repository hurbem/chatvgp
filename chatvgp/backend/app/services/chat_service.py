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
    Usa Claude para extrair categoria e condomínio da pergunta do usuário.
    Retorna (categoria_id, condominio_id) ou (None, None) se não encontrar.
    Para testes, retorna a primeira categoria e condomínio disponíveis.
    """
    categorias = db.query(Categoria).all()
    condominios = db.query(Condominio).all()

    # Debug: verificar token
    token_status = settings.CLAUDE_API_KEY[:20] + "..." if settings.CLAUDE_API_KEY else "VAZIO"
    logger.warning(f"[EXTRACT] CLAUDE_API_KEY: {token_status}")
    logger.warning(f"[EXTRACT] Cliente Anthropic: {client is not None}")
    logger.warning(f"[EXTRACT] Token válido (sk-ant-): {settings.CLAUDE_API_KEY.startswith('sk-ant-')}")
    sys.stdout.flush()

    # Se não há cliente Anthropic ou token inválido, retorna primeiro de cada
    if not client or not settings.CLAUDE_API_KEY.startswith("sk-ant-"):
        logger.warning(f"[EXTRACT] ⚠️ USANDO FALLBACK (sem Claude)")
        sys.stdout.flush()
        return (categorias[0].id if categorias else None,
                condominios[0].id if condominios else None)

    logger.warning(f"[EXTRACT] ✅ USANDO CLAUDE")
    sys.stdout.flush()

    categorias_str = ", ".join([f"{c.id}: {c.nome}" for c in categorias])
    condominios_str = ", ".join([f"{c.id}: {c.nome} ({c.cidade})" for c in condominios])

    prompt = f"""Analise a pergunta do usuário e extraia:
1. A categoria de serviço (ID)
2. O condomínio mencionado (ID), se houver

Pergunta: "{pergunta}"

Categorias disponíveis: {categorias_str}
Condomínios disponíveis: {condominios_str}

Responda APENAS em JSON:
{{"categoria_id": <ID ou null>, "condominio_id": <ID ou null>}}"""

    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        response_text = message.content[0].text
        # Extrair JSON da resposta
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        json_str = response_text[start:end]
        result = json.loads(json_str)
        cat_id = result.get("categoria_id")
        cond_id = result.get("condominio_id")
        logger.warning(f"[EXTRACT] ✅ Claude retornou: categoria_id={cat_id}, condominio_id={cond_id}")
        sys.stdout.flush()
        return cat_id, cond_id
    except Exception as e:
        # Fallback: retorna primeiro de cada
        import traceback
        logger.error(f"[EXTRACT] ❌ Erro ao chamar Claude:")
        logger.error(f"[EXTRACT] Tipo: {type(e).__name__}")
        logger.error(f"[EXTRACT] Mensagem: {str(e)}")
        logger.error(f"[EXTRACT] Traceback:\n{traceback.format_exc()}")
        logger.warning(f"[EXTRACT] ⚠️ USANDO FALLBACK por erro")
        sys.stdout.flush()
        return (categorias[0].id if categorias else None,
                condominios[0].id if condominios else None)

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
