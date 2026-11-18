from sqlalchemy.orm import Session
from app.models import Prestador, Categoria, Log
from typing import Optional
from urllib.parse import quote
import logging
import re
import unicodedata

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
        db.rollback()
        logger.error(f"Erro ao registrar log: {e}")
        # Continua mesmo se falhar a gravação de log


# Palavras muito curtas/comuns que não ajudam a identificar categoria
STOPWORDS = {
    "a", "o", "as", "os", "e", "ou", "de", "da", "do", "das", "dos",
    "em", "no", "na", "nos", "nas", "um", "uma", "uns", "umas",
    "para", "por", "com", "sem", "que", "se",
}


def _remover_acentos(texto: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


def _tokenize(texto: str) -> set:
    """Extrai palavras (>=3 letras, sem stopwords, sem acento) de um texto."""
    palavras = re.findall(r"\w+", _remover_acentos(texto.lower()))
    return {p for p in palavras if len(p) >= 3 and p not in STOPWORDS}


def _pontuar_categoria(cat: Categoria, pergunta_tokens: set) -> int:
    """
    Quantas palavras da pergunta "batem" com a categoria.
    - Nome: cada palavra do nome presente na pergunta conta 1 ponto.
    - Alias: um alias só conta se TODAS as suas palavras estiverem na
      pergunta; vale o número de palavras dele (alias mais específico vale mais).
    """
    pontos_nome = len(_tokenize(cat.nome) & pergunta_tokens)

    pontos_alias = 0
    if cat.aliases:
        for alias in cat.aliases.split(","):
            alias_tokens = _tokenize(alias)
            if alias_tokens and alias_tokens.issubset(pergunta_tokens):
                pontos_alias = max(pontos_alias, len(alias_tokens))

    return max(pontos_nome, pontos_alias)


def extrair_categoria(pergunta: str, db: Session) -> Optional[int]:
    """
    Extrai a categoria da pergunta usando keyword matching
    por palavras inteiras (nome + aliases).
    Escolhe a categoria com mais palavras em comum; em caso de empate,
    vale a de menor 'ordem'.
    Retorna categoria_id (ou None) e registra a busca nos logs.
    """
    categorias = db.query(Categoria).order_by(Categoria.ordem, Categoria.id).all()
    pergunta_tokens = _tokenize(pergunta)

    melhor = None
    melhor_pontos = 0
    for cat in categorias:
        pontos = _pontuar_categoria(cat, pergunta_tokens)
        if pontos > melhor_pontos:  # ">" mantém a primeira (menor ordem) no empate
            melhor, melhor_pontos = cat, pontos

    if melhor is None:
        logger.warning(f"[BUSCA] Categoria não identificada. Pergunta: '{pergunta}'")
        registrar_log(
            db,
            tipo="CATEGORIA_NAO_IDENTIFICADA",
            pergunta=pergunta,
            mensagem="Nenhuma categoria foi identificada na pergunta"
        )
        return None

    registrar_log(
        db,
        tipo="BUSCA_SUCESSO",
        pergunta=pergunta,
        categoria=melhor.nome,
    )
    return melhor.id


def buscar_prestadores(
    db: Session, categoria_id: int, limit: int = 5
) -> list:
    """
    Busca prestadores ativos da categoria.
    Ordem: premium primeiro, depois verificados, depois por nome.
    """
    prestadores = (
        db.query(Prestador)
        .filter(
            Prestador.categorias.any(Categoria.id == categoria_id),
            Prestador.status == "ativo",
        )
        .order_by(
            Prestador.premium.desc(),
            Prestador.verificado_hurbem.desc(),
            Prestador.nome,
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "id": p.id,
            "nome": p.nome,
            "whatsapp": p.whatsapp,
            "descricao": p.descricao,
            "instagram": p.instagram,
            "site": p.site,
            "notas": p.notas,
            "link_whatsapp": gerar_link_whatsapp(p.whatsapp),
            "verificado_hurbem": bool(p.verificado_hurbem),
            "premium": bool(p.premium),
        }
        for p in prestadores
    ]


MENSAGEM_WHATSAPP = "Olá encontrei sua recomendação no chatVGP, estou precisando falar contigo"


def gerar_link_whatsapp(whatsapp: str) -> str:
    """
    Gera link de WhatsApp (wa.me) com mensagem padrão.
    O wa.me exige o número no formato internacional, então números
    brasileiros com DDD (10 ou 11 dígitos) recebem o código do país 55.
    """
    digitos = "".join(filter(str.isdigit, whatsapp or ""))
    if len(digitos) in (10, 11):
        digitos = "55" + digitos
    return f"https://wa.me/{digitos}?text={quote(MENSAGEM_WHATSAPP)}"
