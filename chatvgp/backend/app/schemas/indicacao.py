from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class IndicacaoCreate(BaseModel):
    condominio_id: int
    nome_morador: str
    whatsapp_morador: str

class IndicacaoResponse(BaseModel):
    id: int
    condominio_id: int
    nome_morador: str
    whatsapp_morador: str
    criado_em: Optional[datetime]

    class Config:
        from_attributes = True
