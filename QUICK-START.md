# Quick Start - ChatVGP Local

## Pré-requisitos

- Docker instalado (https://www.docker.com/products/docker-desktop)
- Python 3.9+
- Node.js 18+

---

## Opção 1: Script Automático (Recomendado)

```bash
cd ~/Documents/Claude/Projects/Projeto\ ChatVGP
chmod +x setup-local.sh
./setup-local.sh
```

Pronto! Acesse http://localhost:5173

---

## Opção 2: Passo-a-Passo Manual

### Terminal 1: PostgreSQL
```bash
docker run --name chatvgp-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=chatvgp \
  -p 5432:5432 \
  -d postgres:15

# Verificar
docker ps | grep chatvgp-db
```

### Terminal 2: Backend
```bash
cd chatvgp/backend

# Criar .env
cat > .env << 'EOF'
DATABASE_URL=postgresql://postgres:password@localhost:5432/chatvgp
SECRET_KEY=dev-secret-key-change-in-production
CLAUDE_API_KEY=sk-placeholder-for-testing
ENVIRONMENT=development
DEBUG=True
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://localhost:8000"]
EOF

# Instalar deps
pip install -r requirements.txt

# Rodar
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Esperado:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Terminal 3: Frontend
```bash
cd frontend-vite
npm run dev
```

**Esperado:**
```
➜ Local:   http://localhost:5173/
```

---

## ✅ Verificar Tudo Funcionando

```bash
# Health check do backend
curl http://localhost:8000/health
# {"status":"ok","version":"0.1.0"}

# Swagger UI
open http://localhost:8000/docs

# Frontend
open http://localhost:5173
```

---

## 🎯 Primeiro Teste

1. **Frontend:** http://localhost:5173 (deve carregar)
2. **Admin:** Clique botão 🔐 Admin → Token: `admin-token` → Entrar
3. **Cadastrar:** 
   - Nome: "João Silva"
   - WhatsApp: 11999887766
   - Categoria: Encanaria (ou criar)
   - Condomínio: Vargem Grande (ou criar)
4. **Buscar:** Volte para chat, digite "Preciso de um encanador"
5. **Resultado:** Deve aparecer João Silva com score

---

## 🛑 Parar Tudo

```bash
# Terminal com Backend: Ctrl+C
# Terminal com Frontend: Ctrl+C

# Parar PostgreSQL
docker stop chatvgp-db
docker rm chatvgp-db  # (opcional, remove container)
```

---

## ⚡ Reiniciar PostgreSQL Depois

```bash
docker start chatvgp-db
# (Dados persistem entre restarts)
```

---

## 🔍 Troubleshooting

### "Port 8000 already in use"
```bash
lsof -i :8000
kill -9 <PID>
```

### "Port 5173 already in use"
```bash
lsof -i :5173
kill -9 <PID>
```

### "Cannot connect to database"
```bash
# Verificar se PostgreSQL está rodando
docker ps | grep chatvgp-db

# Se não estiver:
docker start chatvgp-db
sleep 3
```

### "CORS error"
Verifique se `CORS_ORIGINS` no .env inclui `http://localhost:5173`

---

## 📊 Arquitetura Local

```
┌─────────────────────────────────────────┐
│  Frontend (React + Vite)                │
│  http://localhost:5173                  │
│  ↓                                       │
│  Axios HTTP Client                      │
│  ↓                                       │
│  Backend (FastAPI)                      │
│  http://localhost:8000/api              │
│  ↓                                       │
│  Database (PostgreSQL)                  │
│  localhost:5432 (interno)               │
└─────────────────────────────────────────┘
```

---

## 🚀 Próximo Passo

Após tudo funcionando localmente, fazer deploy em produção:
→ Ler `DEPLOY-RENDER-DETALHADO.md`
