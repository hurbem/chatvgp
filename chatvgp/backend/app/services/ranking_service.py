from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Prestador, Feedback
from app.schemas.feedback import FeedbackStats

def calcular_stats_prestador(
    db: Session, prestador_id: int, condominio_id: int
) -> FeedbackStats:
    """
    Calcula estatísticas de um prestador em um condomínio específico.
    """
    feedbacks = db.query(Feedback).filter(
        Feedback.prestador_id == prestador_id,
        Feedback.condominio_id == condominio_id,
    ).all()

    if not feedbacks:
        return FeedbackStats(total_feedbacks=0)

    total = len(feedbacks)
    qualidade_media = sum(f.qualidade for f in feedbacks) / total
    material_acertou = sum(1 for f in feedbacks if f.material_estimativa == "Acertou") / total
    prazo_cumprido = sum(1 for f in feedbacks if f.prazo_manteve) / total
    custo_mantido = sum(1 for f in feedbacks if f.custo_manteve) / total

    # Calcular scores
    score_material = material_acertou * 2
    score_prazo = prazo_cumprido * 1.5
    score_custo = custo_mantido * 1.5
    score_qualidade = qualidade_media

    score_final = score_material + score_prazo + score_custo + score_qualidade

    return FeedbackStats(
        qualidade_media=round(qualidade_media, 1),
        material_acertou_pct=round(material_acertou, 2),
        prazo_cumprido_pct=round(prazo_cumprido, 2),
        custo_mantido_pct=round(custo_mantido, 2),
        total_feedbacks=total,
        score_material=round(score_material, 2),
        score_prazo=round(score_prazo, 2),
        score_custo=round(score_custo, 2),
        score_qualidade=round(score_qualidade, 2),
        score_final=round(score_final, 2),
    )
