import requests
from app.config import settings

def gerar_aliases_com_claude(nome_categoria: str) -> str:
    """
    Usa a Claude API via REST para gerar aliases para uma categoria.
    Retorna uma string com aliases separados por vírgula.
    """
    try:
        print(f"🔑 API Key presente: {bool(settings.CLAUDE_API_KEY)}")
        print(f"🔑 API Key: {settings.CLAUDE_API_KEY[:10]}..." if settings.CLAUDE_API_KEY else "🔑 API Key: VAZIA")

        prompt = f"""Você é um assistente que gera palavras-chave e aliases para categorias de serviços profissionais.

Dada a categoria: "{nome_categoria}"

Gere uma lista de 5-8 aliases ou palavras-chave relacionadas que alguém poderia usar para buscar esse serviço.

Requisitos:
- Palavras-chave relevantes e diretas
- Em português brasileiro
- Separadas por vírgula
- Sem espaços antes/depois das vírgulas
- Minúsculas
- Exemplo format: "palavra1,palavra2,palavra3"

Responda APENAS com a lista de aliases, nada mais."""

        print(f"📤 Enviando prompt para Claude...")

        headers = {
            "x-api-key": settings.CLAUDE_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        data = {
            "model": "claude-sonnet-4-6",
            "max_tokens": 200,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data,
            timeout=30
        )

        response.raise_for_status()
        result = response.json()

        aliases = result["content"][0]["text"].strip()
        print(f"✅ Aliases gerados: {aliases}")
        return aliases

    except Exception as e:
        print(f"❌ ERRO ao gerar aliases com Claude: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return ""  # Retorna vazio se falhar
