from sqlalchemy.orm import Session
from app.config import settings
from app.models import Prestador, Categoria, Condominio, Feedback
from app.services.ranking_service import calcular_stats_prestador
import json

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
            break

    # Keyword matching para condomínios
    condominio_id = None
    for cond in condominios:
        keywords = cond.nome.lower().split() + cond.cidade.lower().split()
        if any(kw in pergunta_lower for kw in keywords):
            condominio_id = cond.id
            break

    # Se não encontrou categoria, retorna a primeira
    if not categoria_id and categorias:
        categoria_id = categorias[0].id

    # Se não encontrou condomínio, retorna o primeiro
    if not condominio_id and condominios:
        condominio_id = condominios[0].id

    return categoria_id, condominio_id

def buscar_prestadores(
    db: Session, categoria_id: int, condominio_id: int = None, limit: int = 5
) -> list:
    """
    Busca prestadores por categoria, ordenados por score agregado.
    """
    query = db.query(Prestador).filter(
        Prestador.categoria_id == categoria_id,
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

        if stats:
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
        else:
            # Prestadores sem feedback ainda retornam com score 0
            prestadores_com_score.append({
                "id": p.id,
                "nome": p.nome,
                "whatsapp": p.whatsapp,
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
