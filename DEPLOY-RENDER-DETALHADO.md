# Deploy Backend em Render — Guia Passo a Passo

## 1. Preparar Backend para Render

### 1.1 Adicionar dependências de produção

**`chatvgp/backend/requirements.txt`** — adicionar:
```
gunicorn==21.2.0
python-multipart==0.0.6
```

### 1.2 Criar `chatvgp/backend/Procfile`

```
web: gunicorn -w 4 -b 0.0.0.0:$PORT app.main:app --worker-class uvicorn.workers.UvicornWorker
```

### 1.3 Atualizar `chatvgp/backend/app/main.py` para produção

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine
from app.routes import chat, prestadores, categorias, condominios, feedback

# Criar tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ChatVGP API",
    description="API para ChatVGP - Busca de prestadores por IA",
    version="0.1.0",
)

# CORS — IMPORTANTE para Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Já vem do .env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(chat.router)
app.include_router(prestadores.router)
app.include_router(categorias.router)
app.include_router(condominios.router)
app.include_router(feedback.router)

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}

@app.get("/")
def root():
    return {"message": "ChatVGP API v0.1.0"}

# Nota: não precisa de if __name__ == "__main__" em Render
```

### 1.4 Verificar `.env.example` está correto

```
DATABASE_URL=postgresql://user:password@localhost:5432/chatvgp
SECRET_KEY=seu-secret-key-aqui
CLAUDE_API_KEY=sk-your-key
ENVIRONMENT=production
DEBUG=False
CORS_ORIGINS=["https://seu-frontend-url.vercel.app"]
```

### 1.5 Commit para GitHub

```bash
cd chatvgp
git add .
git commit -m "Prepare backend for Render deployment"
git push origin main
```

---

## 2. Criar PostgreSQL em Render

### 2.1 Acessar Render Dashboard

1. Ir para https://dashboard.render.com
2. Login/Sign Up

### 2.2 Criar Database

**Topo → New + → PostgreSQL**

Preencher:
- **Name:** `chatvgp-db`
- **Database:** `chatvgp`
- **User:** `postgres`
- **Region:** São Paulo (ou sua região mais próxima)
- **Version:** 15 (padrão)
- **Pricing Plan:** Free (para MVP)

### 2.3 Salvar Connection String

Após criar, você verá na tela:
```
postgresql://postgres:PASSWORD@HOST:5432/chatvgp
```

**Copiar e guardar em lugar seguro** (vai usar no passo 3)

---

## 3. Criar Web Service (Backend) em Render

### 3.1 New Web Service

**Dashboard → New + → Web Service**

### 3.2 Conectar GitHub

- Clica "Connect your repository"
- Seleciona seu repo `chatvgp`

### 3.3 Configurar Build

| Campo | Valor |
|-------|-------|
| **Name** | `chatvgp-api` |
| **GitHub Repo** | seu-usuario/chatvgp |
| **Root Directory** | `chatvgp/backend` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn -w 4 -b 0.0.0.0:$PORT app.main:app --worker-class uvicorn.workers.UvicornWorker` |
| **Pricing Plan** | Free (para MVP) |
| **Region** | São Paulo |

### 3.4 Adicionar Variáveis de Ambiente

**Environment → Add Environment Variable**

Adicionar uma por uma:

```
DATABASE_URL = postgresql://postgres:PASSWORD@HOST:5432/chatvgp
```
(usar connection string do PostgreSQL que criou)

```
SECRET_KEY = gera-uma-secret-muito-longa-aqui
```
(usar comando: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)

```
CLAUDE_API_KEY = sk-your-actual-api-key-here
```

```
ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ENVIRONMENT = production
DEBUG = False
CORS_ORIGINS = ["https://chatvgp.vercel.app", "http://localhost:3000"]
```

### 3.5 Clicar "Create Web Service"

Render começa a build automaticamente.

**Verificar logs:**
- Deve terminar com "Server is running"
- Se erro, ver logs em tempo real

---

## 4. Testar Backend Render

### 4.1 Encontrar URL

Após sucesso, Render gera URL automática:
```
https://chatvgp-api.onrender.com
```

### 4.2 Testar Health Check

```bash
curl https://chatvgp-api.onrender.com/health
# Resposta: {"status":"ok","version":"0.1.0"}
```

### 4.3 Testar Chat

```bash
curl -X POST https://chatvgp-api.onrender.com/api/chat/buscar \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "Preciso de um encanador"}'
```

### 4.4 Testar Database

```bash
curl https://chatvgp-api.onrender.com/docs
```
(Swagger UI deve carregar)

---

## 5. Atualizar Frontend para Apontar Backend Render

### 5.1 Frontend `.env`

**`chatvgp/frontend/.env`:**
```
REACT_APP_API_BASE_URL = https://chatvgp-api.onrender.com/api
```

### 5.2 Commit

```bash
git add chatvgp/frontend/.env
git commit -m "Update frontend API URL to Render backend"
git push origin main
```

---

## 6. Deploy Frontend em Vercel

### 6.1 Acessar Vercel

1. Ir para https://vercel.com/dashboard
2. Login/Sign Up (recomenda GitHub)

### 6.2 Importar Projeto

**Add New → Project → Import Git Repository**

- Seleciona `seu-usuario/chatvgp`
- Clica "Import"

### 6.3 Configurar Build

| Campo | Valor |
|-------|-------|
| **Project Name** | `chatvgp` |
| **Framework** | Create React App |
| **Root Directory** | `chatvgp/frontend` |

### 6.4 Adicionar Variáveis de Ambiente

**Environment Variables:**
```
REACT_APP_API_BASE_URL = https://chatvgp-api.onrender.com/api
```

### 6.5 Deploy

Clica "Deploy"

Vercel começa a build e deploy.

**URL gerada:**
```
https://chatvgp.vercel.app
```

---

## 7. Testar Integração Completa

### 7.1 Frontend Vercel

1. Ir para https://chatvgp.vercel.app
2. Fazer busca: "Preciso de um encanador"
3. Verificar em Dev Tools se chamadas vão para Render

### 7.2 Admin

1. Clica "🔐 Admin"
2. Token: `admin-token`
3. Cadastrar novo prestador
4. Ver lista atualizada

### 7.3 Troubleshooting

**Console error "CORS"?**
- Verificar `CORS_ORIGINS` em Render → Environment
- Deve incluir `https://chatvgp.vercel.app`

**Dados não aparecem?**
- Render cold starts podem levar 30s
- Atualizar página
- Verificar Render logs: Dashboard → chatvgp-api → Logs

**Database vazio?**
- Criar dados via Swagger: `https://chatvgp-api.onrender.com/docs`
- Ou usar curl (ver TESTE-RAPIDO.md)

---

## 8. Configurar Domínio Personalizado (Opcional)

### 8.1 Render Backend

**Dashboard → chatvgp-api → Settings → Custom Domain**

Adicionar domínio (ex: `api.seu-dominio.com`)

Render fornece instruções de DNS

### 8.2 Vercel Frontend

**Dashboard → chatvgp → Settings → Domains**

Adicionar domínio (ex: `chatvgp.seu-dominio.com`)

Vercel guia passo a passo

---

## 9. Monitoramento

### 9.1 Render Logs

**Dashboard → chatvgp-api → Logs**

Ver logs em tempo real

### 9.2 Uptime Monitor (Grátis)

Usar `https://updown.io`:
1. Cadastrar conta
2. Monitorar: `https://chatvgp-api.onrender.com/health`
3. Receber alertas se down

### 9.3 Vercel Analytics (Grátis)

**Dashboard → chatvgp → Analytics**

Ver performance, requests, erros

---

## 10. Próximas Melhorias

- [ ] Upgrade Render para Standard ($12/mês) — remove cold starts
- [ ] Upgrade Database PostgreSQL Standard ($15/mês) — backup automático
- [ ] Email notifications (SendGrid)
- [ ] Sentry for error tracking
- [ ] CDN (Cloudflare)

---

## Checklist Final

- [x] Backend rodando em `https://chatvgp-api.onrender.com`
- [x] PostgreSQL conectado
- [x] Frontend rodando em `https://chatvgp.vercel.app`
- [x] CORS configurado
- [x] Busca funcionando
- [x] Admin funcionando
- [x] Database funcionando

**Parabéns! ChatVGP está em produção! 🚀**
