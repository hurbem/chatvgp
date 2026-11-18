from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Categoria
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import extrair_categoria, buscar_prestadores

router = APIRouter(prefix="/api/chat", tags=["chat"])

SEM_RESULTADO = "Nenhum prestador encontrado para essa busca."


@router.post("/buscar", response_model=ChatResponse)
def buscar(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Endpoint principal: cliente faz pergunta e recebe lista de prestadores.
    """
    pergunta = request.pergunta.strip()
    if not pergunta:
        raise HTTPException(status_code=400, detail="Pergunta não pode estar vazia")

    categoria_id = extrair_categoria(pergunta, db)
    if not categoria_id:
        return ChatResponse(pergunta=pergunta, prestadores=[], total_resultados=0, mensagem=SEM_RESULTADO)

    prestadores = buscar_prestadores(db, categoria_id, limit=5)
    categoria = db.get(Categoria, categoria_id)

    return ChatResponse(
        pergunta=pergunta,
        categoria=categoria.nome if categoria else None,
        prestadores=prestadores,
        total_resultados=len(prestadores),
        mensagem=None if prestadores else SEM_RESULTADO,
    )
