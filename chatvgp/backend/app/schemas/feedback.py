from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class FeedbackBase(BaseModel):
    prestador_id: int
    condominio_id: int
    categoria_id: int
    data_feedback: date
    qualidade: int = Field(ge=1, le=5, description="Nota de 1 a 5")
    material_estimativa: str = Field(
        description="Acertou, Subestimou 10-25%, Subestimou 25-50%, Subestimou >50%"
    )
    prazo_manteve: bool
    custo_manteve: bool
    observacoes: Optional[str] = None
    seu_feedback: bool = False

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackResponse(FeedbackBase):
    id: int
    criado_em: datetime

class FeedbackStats(BaseModel):
    qualidade_media: Optional[float] = None
    material_acertou_pct: Optional[float] = None
    prazo_cumprido_pct: Optional[float] = None
    custo_mantido_pct: Optional[float] = None
    total_feedbacks: int = 0
    score_material: float = 0
    score_prazo: float = 0
    score_custo: float = 0
    score_qualidade: float = 0
    score_final: float = 0
