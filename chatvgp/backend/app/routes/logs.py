from fastapi import APIRouter, HTTPException
import os
import re
from datetime import datetime

router = APIRouter(prefix="/api/logs", tags=["logs"])

@router.get("/buscas-nao-identificadas")
def buscas_nao_identificadas(limit: int = 100):
    """
    Retorna as últimas pesquisas que não tiveram categoria identificada.
    Público (sem autenticação).
    """
    logs_file = "logs/chatvgp.log"

    # Verificar se arquivo de logs existe
    if not os.path.exists(logs_file):
        return {
            "total": 0,
            "logs": [],
            "mensagem": "Nenhum log encontrado ainda"
        }

    try:
        # Ler arquivo de logs
        with open(logs_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Filtrar linhas com "[BUSCA] Categoria não identificada"
        buscas_nao_identificadas = []

        for line in lines:
            if "[BUSCA] Categoria não identificada" in line:
                # Extrair informações da linha
                # Formato: 2026-06-03 16:35:45,123 - app.services.chat_service - WARNING - [BUSCA] Categoria não identificada. Pergunta: 'preciso de um unicórnio'

                try:
                    # Extrair timestamp
                    timestamp_match = re.search(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                    timestamp = timestamp_match.group(1) if timestamp_match else None

                    # Extrair pergunta entre aspas simples
                    pergunta_match = re.search(r"Pergunta: '([^']+)'", line)
                    pergunta = pergunta_match.group(1) if pergunta_match else "desconhecida"

                    buscas_nao_identificadas.append({
                        "timestamp": timestamp,
                        "pergunta": pergunta,
                        "tipo": "CATEGORIA_NAO_IDENTIFICADA"
                    })
                except Exception as e:
                    continue

        # Reverter para mostrar mais recentes primeiro
        buscas_nao_identificadas.reverse()

        # Limitar resultados
        buscas_nao_identificadas = buscas_nao_identificadas[:limit]

        return {
            "total": len(buscas_nao_identificadas),
            "limit": limit,
            "logs": buscas_nao_identificadas
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao ler logs: {str(e)}"
        )

@router.get("/todas")
def todos_os_logs(limit: int = 100):
    """
    Retorna todos os logs da aplicação.
    Público (sem autenticação).
    """
    logs_file = "logs/chatvgp.log"

    if not os.path.exists(logs_file):
        return {
            "total": 0,
            "logs": [],
            "mensagem": "Nenhum log encontrado ainda"
        }

    try:
        with open(logs_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Pegar últimas linhas (mais recentes)
        lines = lines[-limit:]
        lines.reverse()

        return {
            "total": len(lines),
            "limit": limit,
            "logs": lines
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao ler logs: {str(e)}"
        )
