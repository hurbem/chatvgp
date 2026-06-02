# ChatVGP — Deploy em Produção

## Arquitetura de Deploy

```
Frontend (Vercel)           Backend (Render)           Database (Render PostgreSQL)
    ↓                           ↓                              ↓
https://chatvgp.vercel.app → https://api.chatvgp.onrender.com → PostgreSQL 15
```

---

## Pre-requisitos

1. Conta GitHub (repositório do projeto)
2. Conta Render (render.com)
3. Conta Vercel (vercel.com)
4. Conta Claude API key (já tem)

---

## Passo 1: Preparar Repositório GitHub

### 1.1 Criar repositório
```bash
cd ~/path/to/chatvgp
git init
git add .
git commit -m "Initial commit: ChatVGP MVP"
git branch -M main
git remote add origin https://github.com/seu-usuario/chatvgp.git
git push -u origin main
```

### 1.2 Criar arquivo `.gitignore`
```bash
# Backend
chatvgp/backend/.env
chatvgp/backend/venv/
chatvgp/backend/__pycache__/
chatvgp/backend/*.db

# Frontend
chatvgp/frontend/.env
chatvgp/frontend/node_modules/
chatvgp/frontend/build/
chatvgp/frontend/.env.local

# IDE
.vscode/
.idea/
*.swp
```

### 1.3 Criar `chatvgp/backend/Procfile` (para Render)
```
web: gunicorn -w 4 -b 0.0.0.0:$PORT app.main:app --worker-class uvicorn.workers.UvicornWorker
```

---

## Passo 2: Deploy Backend em Render

### 2.1 Acessar Render
1. Ir para https://render.com
2. Fazer login/criar conta
3. Conectar repositório GitHub

### 2.2 Criar PostgreSQL Database

**Dashboard Render → New → PostgreSQL**

Configurações:
- Name: `chatvgp-db`
- Database: `chatvgp`
- User: `postgres` (padrão)
- Keep durante: Free
- Region: São Paulo (ou sua região)

**Salvar connection string (vai precisar)**

### 2.3 Criar Web Service (Backend)

**Dashboard Render → New → Web Service**

Configurações:
- **Name:** `chatvgp-api`
- **GitHub Repo:** seu-usuario/chatvgp
- **Root Directory:** `chatvgp/backend`
- **Runtime:** Python
- **Build Command:** 
  ```
  pip install -r requirements.txt
  ```
- **Start Command:** 
  ```
  gunicorn -w 4 -b 0.0.0.0:$PORT app.main:app --worker-class uvicorn.workers.UvicornWorker
  ```

### 2.4 Configurar Variáveis de Ambiente (Render)

**Environment → Add Environment Variable**

```
DATABASE_URL = postgresql://...RENDER_CONNECTION_STRING
SECRET_KEY = gera-uma-secret-key-muito-longa-aqui
CLAUDE_API_KEY = sk-your-actual-key
ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ENVIRONMENT = production
DEBUG = False
CORS_ORIGINS = ["https://chatvgp.vercel.app"]
```

**Secret Key generator (Python):**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2.5 Deploy

Clica em "Deploy" → Render começa a build automaticamente

**Teste:**
```bash
curl https://chatvgp-api.onrender.com/health
# Resposta: {"status":"ok","version":"0.1.0"}
```

**Swagger UI:** `https://chatvgp-api.onrender.com/docs`

---

## Passo 3: Deploy Frontend em Vercel

### 3.1 Acessar Vercel
1. Ir para https://vercel.com
2. Fazer login/criar conta (recomenda GitHub)
3. Conectar repositório

### 3.2 Criar Projeto

**Add New → Project → Import Git Repository**

Selecionar: seu-usuario/chatvgp

Configurações:
- **Project Name:** `chatvgp`
- **Framework Preset:** Create React App
- **Root Directory:** `chatvgp/frontend`

### 3.3 Configurar Variáveis de Ambiente (Vercel)

**Settings → Environment Variables**

```
REACT_APP_API_BASE_URL = https://chatvgp-api.onrender.com/api
```

### 3.4 Deploy

Clica em "Deploy" → Vercel começa a build

**URL:** `https://chatvgp.vercel.app`

---

## Passo 4: Configurar CORS e Conexões

### 4.1 Atualizar CORS no Backend

**Render → Environment → CORS_ORIGINS**

```json
["https://chatvgp.vercel.app", "http://localhost:3000"]
```

### 4.2 Testar Conexão

1. Abrir `https://chatvgp.vercel.app`
2. Fazer uma busca
3. Verificar em Network (Dev Tools) se chamadas vão para `chatvgp-api.onrender.com`

---

## Passo 5: Domínio Personalizado (Opcional)

### 5.1 Render Backend

**Render → chatvgp-api → Settings → Custom Domain**

Opção A: Use domínio Render  
Opção B: Use domínio próprio
- Exemplo: `api.seu-dominio.com`
- Apontar CNAME em seu registrador DNS

### 5.2 Vercel Frontend

**Vercel → chatvgp → Settings → Domains**

Adicionar domínio (Vercel guia passo a passo para DNS)

---

## Passo 6: Verificação de Produção

### Checklist de Deploy

- [ ] Backend rodando em Render: `https://chatvgp-api.onrender.com/health`
- [ ] Frontend rodando em Vercel: `https://chatvgp.vercel.app`
- [ ] Database PostgreSQL conectado
- [ ] CORS configurado corretamente
- [ ] Claude API key funcionando
- [ ] Login admin funcionando (token)
- [ ] Chat funcionando (busca)
- [ ] Cadastro de prestadores funcionando

### Teste de Ponta a Ponta

1. Acessar frontend: `https://chatvgp.vercel.app`
2. Fazer busca: "Preciso de um encanador"
3. Resultado deve vir do backend
4. Clique em "Contatar via WhatsApp"
5. Acessar Admin: clique "🔐 Admin"
6. Token: qualquer valor (ex: "admin-token")
7. Cadastrar novo prestador

---

## Monitoramento em Produção

### Render

**Dashboard → chatvgp-api → Logs**

Visualiza logs em tempo real

### Vercel

**Dashboard → chatvgp → Deployments**

Histórico de deploys e logs

### Uptime Monitoring (Recomendado)

Usar site grátis como:
- `https://updown.io` (monitor health check)
- `https://statuspage.io` (status page pública)

---

## CI/CD Automático

### GitHub Actions (Opcional)

Criar `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Render
        run: |
          curl https://api.render.com/deploy/srv-${{ secrets.RENDER_SERVICE_ID }}?key=${{ secrets.RENDER_API_KEY }}
```

---

## Troubleshooting Deploy

### Backend não inicia
```
# Verificar logs em Render
- Render → chatvgp-api → Logs
- Procurar por erro de importação ou database connection
```

### Frontend não carrega dados
```
# Dev Tools Console (F12) → Network → Chat request
- Verificar se URL está correta
- Verificar CORS error
- Verificar se backend está online
```

### Database não conecta
```
# Render → PostgreSQL → Info
- Copiar connection string corretamente
- Testar com psql local primeiro:
  psql postgresql://...connection-string
```

### Cold starts lento
```
# Render usa free tier que hiberna
- Solução: upgrade para plano pago
- Ou aceitar que primeiro request é lento
- Usar uptime monitor para manter ativo
```

---

## Upgrade para Produção Real

Quando quiser mais performance:

### Backend (Render)
- [ ] Upgrade de Free para Standard ($12/mês)
- [ ] Database Standard ($15/mês)
- [ ] SSL automático (já incluído)

### Frontend (Vercel)
- [ ] Pro plan ($20/mês) — opcional, free já é bom

---

## Próximos Passos

1. ✅ Deploy Backend + Frontend
2. ⏳ Autenticação JWT em produção
3. ⏳ Certificado SSL (automático no Render/Vercel)
4. ⏳ Email notifications
5. ⏳ Analytics (Google Analytics, Sentry)
6. ⏳ Backup automático database

---

## Resumo URLs de Produção

| Serviço | URL | Tipo |
|---------|-----|------|
| Frontend | https://chatvgp.vercel.app | Público |
| Backend API | https://chatvgp-api.onrender.com | Privado (CORS) |
| API Docs | https://chatvgp-api.onrender.com/docs | Público |
| Admin | https://chatvgp.vercel.app (clique 🔐) | Protegido |

---

## Contatos de Suporte

- **Render Support:** https://support.render.com
- **Vercel Support:** https://vercel.com/support
- **Claude API Issues:** https://support.anthropic.com
