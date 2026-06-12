from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    pergunta: str

class PrestadorResult(BaseModel):
    id: int
    nome: str
    whatsapp: str
    link_whatsapp: str
    instagram: Optional[str] = None
    site: Optional[str] = None
    notas: Optional[str] = None

class ChatResponse(BaseModel):
    pergunta: str
    categoria: Optional[str] = None
    prestadores: List[PrestadorResult]
    total_resultados: int
