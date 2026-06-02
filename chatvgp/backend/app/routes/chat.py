from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse, PrestadorResult
from app.services.chat_service import extrair_categoria_e_condominio, buscar_prestadores
from app.models import Categoria, Condominio

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/buscar")
def buscar(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Endpoint principal: cliente faz pergunta e recebe lista de prestadores.
    """
    if not request.pergunta:
        raise HTTPException(status_code=400, detail="Pergunta não pode estar vazia")

    # Extrair categoria e condomínio da pergunta
    categoria_id, condominio_id = extrair_categoria_e_condominio(request.pergunta, db)

    if not categoria_id:
        return {
            "pergunta": request.pergunta,
            "categoria": None,
            "condominio": None,
            "prestadores": [],
            "total_resultados": 0,
        }

    # Buscar prestadores
    prestadores = buscar_prestadores(db, categoria_id, condominio_id, limit=5)

    # Obter nomes de categoria e condomínio
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    condominio = None
    if condominio_id:
        condominio = db.query(Condominio).filter(Condominio.id == condominio_id).first()

    return {
        "pergunta": request.pergunta,
        "categoria": categoria.nome if categoria else None,
        "condominio": condominio.nome if condominio else None,
        "prestadores": prestadores,
        "total_resultados": len(prestadores),
    }
