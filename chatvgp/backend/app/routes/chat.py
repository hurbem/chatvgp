from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
import sys
from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse, PrestadorResult
from app.services.chat_service import extrair_categoria_e_condominio, buscar_prestadores
from app.models import Categoria, Condominio

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(message)s',
    stream=sys.stdout,
    force=True
)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/buscar")
def buscar(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Endpoint principal: cliente faz pergunta e recebe lista de prestadores.
    """
    logger.warning(f"[CHAT] ➡️ Pergunta recebida: '{request.pergunta}'")
    sys.stdout.flush()

    if not request.pergunta:
        raise HTTPException(status_code=400, detail="Pergunta não pode estar vazia")

    # Extrair categoria e condomínio da pergunta
    logger.warning(f"[CHAT] 🔍 Chamando extrair_categoria_e_condominio...")
    sys.stdout.flush()
    categoria_id, condominio_id = extrair_categoria_e_condominio(request.pergunta, db)
    logger.warning(f"[CHAT] ✅ Resultado: categoria_id={categoria_id}, condominio_id={condominio_id}")
    sys.stdout.flush()

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
