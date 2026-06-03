from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CategoriaBase(BaseModel):
    nome: str
    descricao: Optional[str] = None

class Categoria(CategoriaBase):
    id: int

class PrestadorBase(BaseModel):
    nome: str
    whatsapp: str
    instagram: Optional[str] = None
    site: Optional[str] = None
    categoria_id: int
    status: str = "ativo"
    notas: Optional[str] = None

class PrestadorCreate(PrestadorBase):
    pass

class PrestadorUpdate(BaseModel):
    nome: Optional[str] = None
    whatsapp: Optional[str] = None
    instagram: Optional[str] = None
    site: Optional[str] = None
    categoria_id: Optional[int] = None
    status: Optional[str] = None
    notas: Optional[str] = None

class PrestadorResponse(PrestadorBase):
    id: int
    criado_em: datetime
    categoria: Categoria

class PrestadorComScore(PrestadorResponse):
    score_final: float = 0
    feedback_count: int = 0
    qualidade_media: Optional[float] = None
    material_acertou_pct: Optional[float] = None
    prazo_cumprido_pct: Optional[float] = None
    custo_mantido_pct: Optional[float] = None
