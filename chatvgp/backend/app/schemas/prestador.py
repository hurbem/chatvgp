from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CategoriaBase(BaseModel):
    id: int
    nome: str

class PrestadorBase(BaseModel):
    nome: str
    email: Optional[str] = None
    whatsapp: str
    cpf_cnpj: Optional[str] = None
    categoria_ids: List[int]  # Nova: lista de até 3 categorias
    descricao: Optional[str] = None
    instagram: Optional[str] = None
    site: Optional[str] = None
    status: str = "ativo"
    notas: Optional[str] = None

class PrestadorCreate(PrestadorBase):
    pass

class PrestadorUpdate(BaseModel):
    nome: Optional[str] = None
    whatsapp: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    descricao: Optional[str] = None
    instagram: Optional[str] = None
    site: Optional[str] = None
    status: Optional[str] = None
    notas: Optional[str] = None

class PrestadorResponse(BaseModel):
    id: int
    nome: str
    email: Optional[str] = None
    whatsapp: str
    cpf_cnpj: Optional[str] = None
    descricao: Optional[str] = None
    instagram: Optional[str] = None
    site: Optional[str] = None
    status: str
    notas: Optional[str] = None
    criado_em: datetime
    atualizado_em: datetime
    verificado_hurbem: bool = False
    premium: bool = False
    categorias: List[CategoriaBase] = []

class PrestadorComScore(PrestadorResponse):
    score_final: float = 0
    feedback_count: int = 0
    qualidade_media: Optional[float] = None
    material_acertou_pct: Optional[float] = None
    prazo_cumprido_pct: Optional[float] = None
    custo_mantido_pct: Optional[float] = None
