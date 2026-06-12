from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.categoria_service import gerar_aliases_com_claude
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
def gerar_aliases(request: AliasRequest) -> AliasResponse:
    """
    Endpoint simples para testar geração de aliases via Claude API.

    Exemplo:
    POST /api/aliases/gerar
    {"nome": "Limpeza Residencial"}

    Resposta:
    {"nome": "Limpeza Residencial", "aliases": "limpeza,residencial,casa,..."}
    """
    print(f"\n{'='*60}")
    print(f"🧪 TESTE DE ALIASES")
    print(f"{'='*60}")
    print(f"📝 Categoria: {request.nome}")

    try:
        aliases = gerar_aliases_com_claude(request.nome)

        print(f"✅ Aliases gerados com sucesso!")
        print(f"{'='*60}\n")

        return AliasResponse(
            nome=request.nome,
            aliases=aliases
        )

    except Exception as e:
        print(f"❌ Erro ao gerar aliases: {e}")
        print(f"{'='*60}\n")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar aliases: {str(e)}")
