from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.categoria_service import gerar_aliases_com_claude
from app.utils.security import get_current_admin
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/aliases",
    tags=["aliases"]
)

class AliasRequest(BaseModel):
    nome: str

class AliasResponse(BaseModel):
    nome: str
    aliases: str

@router.post("/gerar")
def gerar_aliases(request: AliasRequest, admin: dict = Depends(get_current_admin)) -> AliasResponse:
    """
    Endpoint simples para testar geração de aliases via Claude API.

    Exemplo:
    POST /api/aliases/gerar
    {"nome": "Limpeza Residencial"}

    Resposta:
    {"nome": "Limpeza Residencial", "aliases": "limpeza,residencial,casa,..."}
    """
    try:
        aliases = gerar_aliases_com_claude(request.nome)
    except Exception as e:
        logger.exception("Erro ao gerar aliases")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar aliases: {e}")

    return AliasResponse(nome=request.nome, aliases=aliases)
