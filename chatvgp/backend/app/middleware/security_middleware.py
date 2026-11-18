"""
Middleware de segurança para bloquear scrapers, bots e LLM
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

# LLM e serviços de IA a bloquear
BLOCKED_LLM = [
    'gpt',
    'claude',
    'bard',
    'llama',
    'cohere',
    'anthropic',
    'openai',
    'chatgpt',
    'gemini',
    'perplexity',
    'grokk',
]

# Scrapers e ferramentas de automação a bloquear
BLOCKED_SCRAPERS = [
    'curl',
    'wget',
    'python-requests',
    'python-urllib',
    'scrapy',
    'mechanize',
    'selenium',
    'puppeteer',
    'phantomjs',
    'headlesschrome',
]

# Rate limiting em memória (IP -> lista de timestamps).
# Obs: cada worker do gunicorn tem sua própria memória, então o limite
# efetivo é aproximadamente (limite x número de workers).
rate_limit_store = defaultdict(list)
RATE_LIMIT_PER_MINUTE = 30
RATE_LIMIT_PER_HOUR = 100

# Limite mais rígido para tentativas de login (dificulta adivinhar a senha)
login_attempts_store = defaultdict(list)
LOGIN_ATTEMPTS_PER_MINUTE = 5
LOGIN_PATH = "/api/auth/login"


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware para proteger contra scrapers, bots e LLM"""

    async def dispatch(self, request: Request, call_next):
        user_agent = request.headers.get('user-agent', '').lower()
        client_ip = request.client.host if request.client else 'unknown'

        # 1. Bloquear requisições sem User-Agent
        if not user_agent or user_agent.strip() == '':
            logger.warning(f"🚫 Bloqueado: Sem User-Agent | IP: {client_ip}")
            return JSONResponse(
                status_code=403,
                content={"detail": "Acesso negado: User-Agent inválido"}
            )

        # 2. Bloquear LLM (IA)
        if self._is_llm(user_agent):
            logger.warning(f"🚫 Bloqueado: LLM detectado | IP: {client_ip} | UA: {user_agent}")
            return JSONResponse(
                status_code=403,
                content={"detail": "Acesso negado: Serviços de IA não permitidos"}
            )

        # 3. Bloquear Scrapers
        if self._is_scraper(user_agent):
            logger.warning(f"🚫 Bloqueado: Scraper detectado | IP: {client_ip} | UA: {user_agent}")
            return JSONResponse(
                status_code=403,
                content={"detail": "Acesso negado: Scrapers não permitidos"}
            )

        # 4. Rate Limiting
        if request.url.path == LOGIN_PATH and not self._check_login_limit(client_ip):
            logger.warning(f"🚫 Bloqueado: muitas tentativas de login | IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={"detail": "Muitas tentativas de login. Aguarde um minuto."}
            )

        if not self._check_rate_limit(client_ip):
            logger.warning(f"🚫 Bloqueado: Rate limit excedido | IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={"detail": "Muitas requisições. Tente novamente mais tarde."}
            )

        # 5. Request OK, adicionar headers de segurança
        response = await call_next(request)

        # Headers de segurança
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        logger.info(f"✅ Requisição OK | IP: {client_ip} | Path: {request.url.path}")

        return response

    @staticmethod
    def _is_llm(user_agent: str) -> bool:
        """Detecta se é requisição de LLM/IA"""
        return any(llm in user_agent for llm in BLOCKED_LLM)

    @staticmethod
    def _is_scraper(user_agent: str) -> bool:
        """Detecta se é requisição de scraper/automação"""
        return any(scraper in user_agent for scraper in BLOCKED_SCRAPERS)

    @staticmethod
    def _check_login_limit(client_ip: str) -> bool:
        """Verifica se IP excedeu o limite de tentativas de login por minuto"""
        now = datetime.now()
        tentativas = [
            ts for ts in login_attempts_store[client_ip]
            if (now - ts) < timedelta(minutes=1)
        ]
        if len(tentativas) >= LOGIN_ATTEMPTS_PER_MINUTE:
            login_attempts_store[client_ip] = tentativas
            return False
        tentativas.append(now)
        login_attempts_store[client_ip] = tentativas
        return True

    @staticmethod
    def _limpar_ips_antigos(now: datetime) -> None:
        """Remove da memória IPs sem requisições na última hora (evita crescer para sempre)."""
        for store, janela in ((rate_limit_store, timedelta(hours=1)),
                              (login_attempts_store, timedelta(minutes=1))):
            for ip in [ip for ip, ts in store.items() if not ts or (now - ts[-1]) >= janela]:
                del store[ip]

    @staticmethod
    def _check_rate_limit(client_ip: str) -> bool:
        """Verifica se IP excedeu rate limit"""
        now = datetime.now()

        # De vez em quando, limpa IPs inativos
        if len(rate_limit_store) > 1000:
            SecurityMiddleware._limpar_ips_antigos(now)

        # Limpar timestamps antigos (> 1 hora)
        rate_limit_store[client_ip] = [
            ts for ts in rate_limit_store[client_ip]
            if (now - ts) < timedelta(hours=1)
        ]

        # Verificar limite por hora
        if len(rate_limit_store[client_ip]) >= RATE_LIMIT_PER_HOUR:
            return False

        # Verificar limite por minuto
        recent = [
            ts for ts in rate_limit_store[client_ip]
            if (now - ts) < timedelta(minutes=1)
        ]
        if len(recent) >= RATE_LIMIT_PER_MINUTE:
            return False

        # Adicionar timestamp atual
        rate_limit_store[client_ip].append(now)

        return True
