from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    pergunta: str
    condominio_id: Optional[int] = None

class PrestadorResult(BaseModel):
    id: int
    nome: str
    whatsapp: str
    link_whatsapp: str
    score_final: float
    feedback_count: int
    qualidade_media: Optional[float]
    material_acertou_pct: Optional[float]
    prazo_cumprido_pct: Optional[float]
    custo_mantido_pct: Optional[float]

class ChatResponse(BaseModel):
    pergunta: str
    categoria: Optional[str] = None
    condominio: Optional[str] = None
    prestadores: List[PrestadorResult]
    total_resultados: int
