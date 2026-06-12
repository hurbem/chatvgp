from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse, PrestadorResult
from app.services.chat_service import extrair_categoria, buscar_prestadores
from app.models import Categoria

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/buscar")
def buscar(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Endpoint principal: cliente faz pergunta e recebe lista de prestadores.
    """
    if not request.pergunta:
        raise HTTPException(status_code=400, detail="Pergunta não pode estar vazia")

    # Extrair categoria da pergunta
    categoria_id = extrair_categoria(request.pergunta, db)

    if not categoria_id:
        return {
            "pergunta": request.pergunta,
            "mensagem": "Nenhum prestador encontrado para essa busca.",
            "categoria": None,
            "condominio": None,
            "prestadores": [],
            "total_resultados": 0,
        }

    # Buscar prestadores
    prestadores = buscar_prestadores(db, categoria_id, limit=5)

    # Obter nome da categoria
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()

    response = {
        "pergunta": request.pergunta,
        "categoria": categoria.nome if categoria else None,
        "condominio": None,
        "prestadores": prestadores,
        "total_resultados": len(prestadores),
    }

    # Adicionar mensagem se não encontrou prestadores
    if not prestadores:
        response["mensagem"] = "Nenhum prestador encontrado para essa busca."

    return response
