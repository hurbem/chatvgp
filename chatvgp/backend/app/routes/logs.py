from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Log
from app.utils.security import get_current_admin
from sqlalchemy import desc

router = APIRouter(prefix="/api/logs", tags=["logs"])

@router.get("/buscas-nao-identificadas")
def buscas_nao_identificadas(limit: int = 100, db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    """
    Retorna as últimas pesquisas que não tiveram categoria identificada.
    Admin only (requer token).
    """
    try:
        logs = db.query(Log).filter(
            Log.tipo == "CATEGORIA_NAO_IDENTIFICADA"
        ).order_by(desc(Log.criado_em)).limit(limit).all()

        return {
            "total": len(logs),
            "limit": limit,
            "logs": [
                {
                    "id": log.id,
                    "timestamp": log.criado_em.isoformat() if log.criado_em else None,
                    "pergunta": log.pergunta,
                    "tipo": log.tipo,
                    "mensagem": log.mensagem
                }
                for log in logs
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao ler logs: {str(e)}"
        )

@router.get("/buscas-sucesso")
def buscas_com_sucesso(limit: int = 100, db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    """
    Retorna as últimas pesquisas que tiveram categoria identificada com sucesso.
    Admin only (requer token).
    """
    try:
        logs = db.query(Log).filter(
            Log.tipo == "BUSCA_SUCESSO"
        ).order_by(desc(Log.criado_em)).limit(limit).all()

        return {
            "total": len(logs),
            "limit": limit,
            "logs": [
                {
                    "id": log.id,
                    "timestamp": log.criado_em.isoformat() if log.criado_em else None,
                    "pergunta": log.pergunta,
                    "categoria": log.categoria_encontrada,
                    "tipo": log.tipo
                }
                for log in logs
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao ler logs: {str(e)}"
        )

@router.get("/todas")
def todos_os_logs(limit: int = 100, db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    """
    Retorna todos os logs da aplicação.
    Admin only (requer token).
    """
    try:
        logs = db.query(Log).order_by(desc(Log.criado_em)).limit(limit).all()

        return {
            "total": len(logs),
            "limit": limit,
            "logs": [
                {
                    "id": log.id,
                    "timestamp": log.criado_em.isoformat() if log.criado_em else None,
                    "tipo": log.tipo,
                    "pergunta": log.pergunta,
                    "categoria": log.categoria_encontrada,
                    "mensagem": log.mensagem
                }
                for log in logs
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao ler logs: {str(e)}"
        )

@router.get("/estatisticas")
def estatisticas_logs(db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    """
    Retorna estatísticas gerais dos logs.
    Admin only (requer token).
    """
    try:
        total_logs = db.query(Log).count()
        nao_identificadas = db.query(Log).filter(Log.tipo == "CATEGORIA_NAO_IDENTIFICADA").count()
        sucesso = db.query(Log).filter(Log.tipo == "BUSCA_SUCESSO").count()

        return {
            "total_logs": total_logs,
            "buscas_nao_identificadas": nao_identificadas,
            "buscas_com_sucesso": sucesso,
            "taxa_sucesso_pct": round((sucesso / total_logs * 100), 2) if total_logs > 0 else 0
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao calcular estatísticas: {str(e)}"
        )
