# ChatVGP — Rodar Local (Passo a Passo)

## Pré-requisitos

- Python 3.9+
- Node.js 16+
- PostgreSQL 13+ (ou Docker)
- Git

---

## Passo 1: Setup PostgreSQL

### Opção A: PostgreSQL Local (macOS com Homebrew)

```bash
# Instalar
brew install postgresql

# Iniciar serviço
brew services start postgresql

# Criar banco de dados
createdb chatvgp

# Verificar
psql -U postgres -d chatvgp
# Deve entrar no prompt do postgres
# Sair: \q
```

### Opção B: PostgreSQL via Docker (Mais Fácil)

```bash
# Executar container
docker run --name chatvgp-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=chatvgp \
  -p 5432:5432 \
  -d postgres:15

# Verificar se está rodando
docker ps
```

Se já rodou antes e quer ligar de novo:
```bash
docker start chatvgp-db
```

---

## Passo 2: Setup Backend

### 2.1 Abrir Terminal 1 (Backend)

```bash
cd ~/Documents/Claude/Projects/Projeto\ ChatVGP/chatvgp/backend
```

### 2.2 Criar Virtual Environment

```bash
# Criar venv
python3 -m venv venv

# Ativar
source venv/bin/activate
# (No Windows: venv\Scripts\activate)

# Verificar se ativou (deve ter (venv) no início da linha)
```

### 2.3 Instalar Dependências

```bash
pip install -r requirements.txt
```

(Vai levar ~2 minutos)

### 2.4 Criar `.env`

```bash
cp .env.example .env
```

**Editar `.env` com seu editor:**

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/chatvgp
SECRET_KEY=seu-secret-key-super-secreto-aqui
CLAUDE_API_KEY=sk-your-actual-claude-api-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=development
DEBUG=True
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

**Importante:** Usar Claude API key real (pega em https://console.anthropic.com)

### 2.5 Rodar Servidor Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Deve aparecer:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 2.6 Testar Backend

**Novo terminal (ou aba):**

```bash
# Health check
curl http://localhost:8000/health

# Deve retornar:
{"status":"ok","version":"0.1.0"}
```

**Swagger UI:** http://localhost:8000/docs

---

## Passo 3: Setup Frontend

### 3.1 Abrir Terminal 2 (Frontend)

```bash
cd ~/Documents/Claude/Projects/Projeto\ ChatVGP/chatvgp/frontend
```

### 3.2 Instalar Dependências

```bash
npm install
```

(Vai levar ~3 minutos)

### 3.3 Criar `.env`

```bash
cp .env.example .env
```

**Conteúdo (já está correto por padrão):**
```
REACT_APP_API_BASE_URL=http://localhost:8000/api
```

### 3.4 Rodar Frontend

```bash
npm start
```

**Deve abrir automaticamente em:** http://localhost:3000

Se não abrir, acesse manualmente.

---

## Passo 4: Testar o Sistema Completo

### 4.1 Criar Dados Iniciais

**Opção A: Via Swagger (Mais Fácil)**

1. Acesse: http://localhost:8000/docs
2. Expandir "POST /api/categorias"
3. Clique "Try it out"
4. Body:
```json
{
  "nome": "Encanaria",
  "descricao": "Serviços hidráulicos"
}
```
5. Clique "Execute"

**Repetir para mais categorias:**
- Eletricista
- Limpeza

### 4.2 Criar Condomínios

**Via Swagger:**

1. POST /api/condominios
2. Body:
```json
{
  "nome": "Condomínio A",
  "cidade": "Vargem Grande Paulista"
}
```

**Repetir:**
```json
{
  "nome": "Condomínio B",
  "cidade": "Vargem Grande Paulista"
}
```

### 4.3 Criar Prestadores

**Via Swagger:**

1. POST /api/prestadores
2. Headers (importante!): Adicionar `Authorization: token`
   - Nome do header: `Authorization`
   - Valor: `token`
3. Body:
```json
{
  "nome": "João Silva",
  "whatsapp": "11999887766",
  "categoria_id": 1,
  "condominio_ids": [1, 2],
  "status": "ativo",
  "notas": "Excelente encanador"
}
```

### 4.4 Criar Feedback

**Via Swagger:**

1. POST /api/feedback
2. Headers: `Authorization: token`
3. Body:
```json
{
  "prestador_id": 1,
  "condominio_id": 1,
  "categoria_id": 1,
  "data_feedback": "2026-02-15",
  "qualidade": 5,
  "material_estimativa": "Acertou",
  "prazo_manteve": true,
  "custo_manteve": true,
  "observacoes": "Excelente serviço",
  "seu_feedback": true
}
```

### 4.5 Testar Chat Frontend

1. Acesse: http://localhost:3000
2. Digite: "Preciso de um encanador em Vargem Grande"
3. Clique "Buscar"
4. Deve retornar João Silva com score

### 4.6 Testar Admin

1. Clique "🔐 Admin" (botão flutuante)
2. Token: `admin-token` (qualquer valor)
3. Veja a lista de prestadores
4. Cadastre novo prestador

---

## Passo 5: Scripts Rápidos (Opcional)

**Criar arquivo `run-local.sh` na raiz do projeto:**

```bash
#!/bin/bash

# Iniciar PostgreSQL (se Docker)
echo "🐘 Iniciando PostgreSQL..."
docker start chatvgp-db 2>/dev/null || docker run --name chatvgp-db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=chatvgp -p 5432:5432 -d postgres:15

sleep 2

# Iniciar Backend
echo "⚙️ Iniciando Backend..."
cd chatvgp/backend
source venv/bin/activate
uvicorn app.main:app --reload &
BACKEND_PID=$!

sleep 3

# Iniciar Frontend
echo "⚛️ Iniciando Frontend..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo ""
echo "✅ Tudo rodando!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
echo "Docs: http://localhost:8000/docs"
echo ""
echo "Pressione Ctrl+C para parar"
wait
```

**Usar:**
```bash
chmod +x run-local.sh
./run-local.sh
```

---

## Troubleshooting

### "Port 8000 already in use"
```bash
# Encontrar processo usando porta 8000
lsof -i :8000

# Matar processo
kill -9 <PID>

# Ou mudar porta
uvicorn app.main:app --reload --port 8001
```

### "Port 3000 already in use"
```bash
# Encontrar
lsof -i :3000

# Matar
kill -9 <PID>

# Ou mudar no frontend .env
REACT_APP_PORT=3001
npm start
```

### "Cannot connect to database"
```bash
# Verificar se PostgreSQL está rodando
pg_isready -h localhost

# Se Docker
docker ps

# Verificar DATABASE_URL no .env
# Deve ser: postgresql://postgres:password@localhost:5432/chatvgp
```

### "Claude API returns error"
```bash
# Verificar CLAUDE_API_KEY
# Pegar em: https://console.anthropic.com

# Verificar se está ativo (não expirado)

# Testar com curl
curl -H "x-api-key: sk-..." https://api.anthropic.com/
```

### "CORS error no frontend"
```bash
# Verificar CORS_ORIGINS no .env backend
CORS_ORIGINS=["http://localhost:3000"]

# Reiniciar backend após mudança
```

### "Frontend não conecta ao backend"
```bash
# Verificar REACT_APP_API_BASE_URL no frontend .env
REACT_APP_API_BASE_URL=http://localhost:8000/api

# Verificar se backend está rodando
curl http://localhost:8000/health

# Verificar console do browser (F12)
```

---

## Parar Tudo

**Terminal Backend:** `Ctrl+C`

**Terminal Frontend:** `Ctrl+C`

**PostgreSQL (Docker):**
```bash
docker stop chatvgp-db
```

---

## Status Esperado

Quando tudo está rodando:

| Serviço | URL | Status |
|---------|-----|--------|
| Frontend | http://localhost:3000 | ✅ React app |
| Backend | http://localhost:8000 | ✅ FastAPI |
| Docs | http://localhost:8000/docs | ✅ Swagger UI |
| Database | localhost:5432 | ✅ PostgreSQL |

---

## Próximos Passos

1. ✅ Rodar localmente
2. Criar dados de teste (prestadores, feedback)
3. Testar chat
4. Testar admin
5. Fazer mudanças/experimentos
6. Fazer deploy

---

## Dúvidas?

Verificar:
- `SETUP-COMPLETO.md` — Setup detalhado
- `API-ENDPOINTS.md` — Como usar endpoints
- `TESTE-RAPIDO.md` — Curl commands
- `PROJETO-COMPLETO.md` — Status geral

**Dica:** Deixar 3 terminais abertos:
1. Backend
2. Frontend
3. Geral (para rodar commands)
