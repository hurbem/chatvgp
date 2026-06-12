from sqlalchemy.orm import Session
from app.config import settings
from app.models import Prestador, Categoria, Log
import json
import logging
import re

logger = logging.getLogger(__name__)

def registrar_log(db: Session, tipo: str, pergunta: str = None, categoria: str = None, mensagem: str = None):
    """
    Registra um log de busca no banco de dados.
    """
    try:
        novo_log = Log(
            tipo=tipo,
            pergunta=pergunta,
            categoria_encontrada=categoria,
            mensagem=mensagem
        )
        db.add(novo_log)
        db.commit()
    except Exception as e:
        logger.error(f"Erro ao registrar log: {e}")
        # Continua mesmo se falhar a gravação de log


# Palavras muito curtas/comuns que não ajudam a identificar categoria ou condomínio
STOPWORDS = {
    "a", "o", "as", "os", "e", "ou", "de", "da", "do", "das", "dos",
    "em", "no", "na", "nos", "nas", "um", "uma", "uns", "umas",
    "para", "por", "com", "sem", "que", "se",
}


def _tokenize(texto: str) -> set:
    """Extrai palavras (>=3 letras, sem stopwords) de um texto."""
    palavras = re.findall(r"\w+", texto.lower())
    return {p for p in palavras if len(p) >= 3 and p not in STOPWORDS}


def extrair_categoria(pergunta: str, db: Session) -> int:
    """
    Extrai a categoria da pergunta usando keyword matching
    por palavras inteiras (nome + aliases).
    Retorna categoria_id (ou None).
    Registra logs de pesquisas não identificadas no banco.
    """
    categorias = db.query(Categoria).all()

    pergunta_tokens = _tokenize(pergunta)

    # Keyword matching para categorias (nome + aliases)
    categoria_id = None
    categoria_nome = None
    for cat in categorias:
        # Procura no nome da categoria (palavras inteiras)
        keywords = _tokenize(cat.nome)
        if keywords & pergunta_tokens:
            categoria_id = cat.id
            categoria_nome = cat.nome
            break

        # Procura nos aliases se tiver (cada alias pode ter mais de uma palavra)
        if cat.aliases:
            aliases = [alias.strip() for alias in cat.aliases.lower().split(',') if alias.strip()]
            for alias in aliases:
                alias_tokens = _tokenize(alias)
                if alias_tokens and alias_tokens.issubset(pergunta_tokens):
                    categoria_id = cat.id
                    categoria_nome = cat.nome
                    break
            if categoria_id:
                break

    # Se não encontrou categoria, registra log e retorna None
    if not categoria_id:
        logger.warning(f"[BUSCA] Categoria não identificada. Pergunta: '{pergunta}'")
        registrar_log(
            db,
            tipo="CATEGORIA_NAO_IDENTIFICADA",
            pergunta=pergunta,
            mensagem="Nenhuma categoria foi identificada na pergunta"
        )
    else:
        # Registra busca bem-sucedida
        registrar_log(
            db,
            tipo="BUSCA_SUCESSO",
            pergunta=pergunta,
            categoria=categoria_nome,
        )

    return categoria_id

def buscar_prestadores(
    db: Session, categoria_id: int, limit: int = 5
) -> list:
    """
    Busca prestadores por categoria, ordenados por score agregado.
    """
    query = db.query(Prestador).filter(
        Prestador.categorias.any(Categoria.id == categoria_id),
        Prestador.status == "ativo",
    )

    prestadores = query.all()

    resultado = []
    for p in prestadores:
        resultado.append({
            "id": p.id,
            "nome": p.nome,
            "whatsapp": p.whatsapp,
            "instagram": p.instagram,
            "site": p.site,
            "notas": p.notas,
            "link_whatsapp": gerar_link_whatsapp(p.whatsapp),
        })

    return resultado[:limit]

def gerar_link_whatsapp(whatsapp: str) -> str:
    """
    Gera link de WhatsApp com mensagem padrão.
    """
    mensagem = "Olá encontrei sua recomendação no chatVGP, estou precisando falar contigo"
    # Remove caracteres especiais do whatsapp
    whatsapp_limpo = "".join(filter(str.isdigit, whatsapp))
    return f"https://wa.me/{whatsapp_limpo}?text={mensagem.replace(' ', '%20')}"
