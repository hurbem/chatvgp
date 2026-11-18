# ChatVGP

Busca de prestadores de serviço em Vargem Grande Paulista-SP. O usuário escreve o que precisa ("preciso de um encanador") e recebe prestadores da categoria com link direto para o WhatsApp.

## Arquitetura

```
Frontend (React, create-react-app)   Backend (FastAPI)            Banco
└── Vercel                           └── Render (Docker)          └── PostgreSQL (Render)
```

- **Frontend:** https://chatvgp.vercel.app
- **API:** https://chatvgp-api.onrender.com (documentação interativa em `/docs`)

## Como a busca funciona

1. A pergunta é quebrada em palavras (sem acento, ignorando palavras curtas como "de", "um").
2. Cada categoria recebe pontos pelas palavras em comum com o **nome** ou com um **alias** (um alias só conta se todas as suas palavras estiverem na pergunta).
3. Vence a categoria com mais pontos; no empate, a de menor `ordem`.
4. Retorna até 5 prestadores **ativos** da categoria: premium primeiro, depois verificados, depois por nome.

Os aliases são gerados pelo Claude quando a categoria é criada (`CLAUDE_API_KEY`).

## Fluxo de cadastro

1. O prestador se cadastra pelo site → entra com status **`pendente`** (não aparece na busca).
2. O admin vê os pendentes em `GET /api/prestadores/admin/lista`.
3. O admin aprova com `PATCH /api/prestadores/{id}/ativar`.

## Endpoints

| Método | Rota | Acesso |
|---|---|---|
| POST | `/api/chat/buscar` `{"pergunta": "..."}` | público |
| GET | `/api/categorias` | público |
| GET | `/api/prestadores`, `/api/prestadores/{id}` | público (só ativos, sem email/CPF) |
| POST | `/api/prestadores` | público (entra como pendente) |
| POST | `/api/prestadores/{id}/clique-whatsapp` | público |
| POST | `/api/auth/login` `{"senha": "<ADMIN_PASSWORD>"}` | público (5 tentativas/min) |
| GET | `/api/prestadores/admin/lista?status_filter=pendente` | admin |
| GET | `/api/prestadores/admin/{id}` | admin |
| PUT / DELETE | `/api/prestadores/{id}` | admin |
| PATCH | `/api/prestadores/{id}/ativar` | admin |
| POST / PUT / DELETE | `/api/categorias...` | admin |
| GET | `/api/logs/...` | admin |

Rotas de admin exigem o header `Authorization: Bearer <token>`, obtido no login.

## Variáveis de ambiente (backend)

| Variável | Descrição |
|---|---|
| `DATABASE_URL` | URL do PostgreSQL |
| `SECRET_KEY` | Chave de assinatura dos tokens JWT |
| `ADMIN_PASSWORD` | Senha de login do admin (mín. 16 caracteres, diferente da `SECRET_KEY`) |
| `ENVIRONMENT` | `production` no Render — o app **não sobe** se as duas chaves acima estiverem ausentes/fracas |
| `CLAUDE_API_KEY` | Para gerar aliases de categorias (opcional) |
| `CORS_ORIGINS` | Origens permitidas, separadas por vírgula |

Gere chaves com: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`

**Nunca** coloque senhas ou chaves em arquivos do repositório.

## Rodando localmente

```bash
# Backend
cd chatvgp/backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # e preencha
uvicorn app.main:app --reload

# Testes
pytest

# Frontend
cd chatvgp/frontend
npm install
npm start   # usa REACT_APP_API_URL ou http://localhost:8000
```

Para ter dados de exemplo no banco local: `psql "<DATABASE_URL local>" -f chatvgp/backend/scripts/seed_local.sql` (⚠️ nunca em produção).

## Criar categorias

```bash
ADMIN_PASSWORD='sua-senha' ./chatvgp/backend/scripts/add-categoria.sh \
  "Banho e Tosa" "Banho, tosa e higiene para pets." \
  "Aluguel Mesas e Cadeiras" "Aluguel de mesas e cadeiras para eventos."
```

Os aliases de busca são gerados pelo Claude automaticamente.

## Deploy

Push no `main` → Render (backend) e Vercel (frontend) fazem o deploy sozinhos.

**Render (`chatvgp-api`)**
- Runtime: **Docker**, usando o `Dockerfile` da raiz do repositório
- Dependências: `chatvgp/backend/requirements-render.txt`
- Comando de start: o `CMD` do `Dockerfile` (gunicorn com 4 workers e `--forwarded-allow-ips`, para o rate limit ver o IP real do usuário)
- Environment: as variáveis da tabela acima

**Vercel (`chatvgp`)**
- Root Directory: `chatvgp/frontend` · Framework: Create React App
- Environment: `REACT_APP_API_URL=https://chatvgp-api.onrender.com`
