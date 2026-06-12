from sqlalchemy.orm import Session
from app.config import settings
from app.models import Prestador, Categoria, Feedback, Log
from app.services.ranking_service import calcular_stats_prestador
import json
import logging
import re

logger = logging.getLogger(__name__)

def registrar_log(db: Session, tipo: str, pergunta: str = None, categoria: str = None, condominio: str = None, mensagem: str = None):
    """
    Registra um log de busca no banco de dados.
    """
    try:
        novo_log = Log(
            tipo=tipo,
            pergunta=pergunta,
            categoria_encontrada=categoria,
            condominio_encontrado=condominio,
            mensagem=mensagem
        )
        db.add(novo_log)
        db.commit()
    except Exception as e:
        logger.error(f"Erro ao registrar log: {e}")
        # Continua mesmo se falhar a gravação de log


# Palavras muito curtas/comuns que não ajudam a identificar categoria ou condomínio
STOPWORDS = {
    "a", "o", "as", "os", "e", "ou", "de", "da", "do", "das", "dos",
    "em", "no", "na", "nos", "nas", "um", "uma", "uns", "umas",
    "para", "por", "com", "sem", "que", "se",
}


def _tokenize(texto: str) -> set:
    """Extrai palavras (>=3 letras, sem stopwords) de um texto."""
    palavras = re.findall(r"\w+", texto.lower())
    return {p for p in palavras if len(p) >= 3 and p not in STOPWORDS}


def extrair_categoria(pergunta: str, db: Session) -> int:
    """
    Extrai a categoria da pergunta usando keyword matching
    por palavras inteiras (nome + aliases).
    Retorna categoria_id (ou None).
    Registra logs de pesquisas não identificadas no banco.
    """
    categorias = db.query(Categoria).all()

    pergunta_tokens = _tokenize(pergunta)

    # Keyword matching para categorias (nome + aliases)
    categoria_id = None
    categoria_nome = None
    for cat in categorias:
        # Procura no nome da categoria (palavras inteiras)
        keywords = _tokenize(cat.nome)
        if keywords & pergunta_tokens:
            categoria_id = cat.id
            categoria_nome = cat.nome
            break

        # Procura nos aliases se tiver (cada alias pode ter mais de uma palavra)
        if cat.aliases:
            aliases = [alias.strip() for alias in cat.aliases.lower().split(',') if alias.strip()]
            for alias in aliases:
                alias_tokens = _tokenize(alias)
                if alias_tokens and alias_tokens.issubset(pergunta_tokens):
                    categoria_id = cat.id
                    categoria_nome = cat.nome
                    break
            if categoria_id:
                break

    # Se não encontrou categoria, registra log e retorna None
    if not categoria_id:
        logger.warning(f"[BUSCA] Categoria não identificada. Pergunta: '{pergunta}'")
        registrar_log(
            db,
            tipo="CATEGORIA_NAO_IDENTIFICADA",
            pergunta=pergunta,
            mensagem="Nenhuma categoria foi identificada na pergunta"
        )
    else:
        # Registra busca bem-sucedida
        registrar_log(
            db,
            tipo="BUSCA_SUCESSO",
            pergunta=pergunta,
            categoria=categoria_nome,
        )

    return categoria_id

def buscar_prestadores(
    db: Session, categoria_id: int, condominio_id: int = None, limit: int = 5
) -> list:
    """
    Busca prestadores por categoria, ordenados por score agregado.
    """
    query = db.query(Prestador).filter(
        Prestador.categorias.any(Categoria.id == categoria_id),
        Prestador.status == "ativo",
    )

    prestadores = query.all()

    # Calcular scores agregados
    prestadores_com_score = []
    for p in prestadores:
        # Se condominio_id foi especificado, calcula score para esse condomínio
        if condominio_id:
            stats = calcular_stats_prestador(db, p.id, condominio_id)
        else:
            # Senão, calcula agregado de todos os feedbacks
            feedbacks = db.query(Feedback).filter(Feedback.prestador_id == p.id).all()
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

        # Sempre adiciona o prestador, com ou sem feedback
        if stats:
            prestadores_com_score.append({
                "id": p.id,
                "nome": p.nome,
                "whatsapp": p.whatsapp,
                "instagram": p.instagram,
                "site": p.site,
                "notas": p.notas,
                "link_whatsapp": gerar_link_whatsapp(p.whatsapp),
                "score_final": stats.score_final,
                "feedback_count": stats.total_feedbacks,
                "qualidade_media": stats.qualidade_media,
                "material_acertou_pct": stats.material_acertou_pct,
                "prazo_cumprido_pct": stats.prazo_cumprido_pct,
                "custo_mantido_pct": stats.custo_mantido_pct,
            })
        else:
            # Prestadores sem feedback retornam com score 0
            prestadores_com_score.append({
                "id": p.id,
                "nome": p.nome,
                "whatsapp": p.whatsapp,
                "instagram": p.instagram,
                "site": p.site,
                "notas": p.notas,
                "link_whatsapp": gerar_link_whatsapp(p.whatsapp),
                "score_final": 0,
                "feedback_count": 0,
                "qualidade_media": None,
                "material_acertou_pct": None,
                "prazo_cumprido_pct": None,
                "custo_mantido_pct": None,
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
