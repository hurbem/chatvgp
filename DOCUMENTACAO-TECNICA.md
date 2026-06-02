# ChatVGP - Documentação Técnica

**Versão:** 1.0.0  
**Data:** Junho 2026  
**Status:** MVP Funcional

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Stack Técnico](#stack-técnico)
3. [Arquitetura](#arquitetura)
4. [Componentes](#componentes)
5. [APIs](#apis)
6. [Setup Local](#setup-local)
7. [Deploy](#deploy)
8. [Troubleshooting](#troubleshooting)
9. [Roadmap](#roadmap)

---

## 🎯 Visão Geral

**ChatVGP** é uma plataforma de busca e recomendação de prestadores de serviços baseada em IA. O sistema:

- Recebe perguntas em linguagem natural
- Usa Claude AI para entender a intenção
- Busca prestadores relevantes no banco de dados
- Calcula scores baseado em feedback histórico
- Retorna recomendações ordenadas por qualidade

**Caso de uso:** Condomínios em Vargem Grande Paulista e Cotia que precisam encontrar encanadores, eletricistas, etc.

---

## 🛠 Stack Técnico

### Frontend
- **Framework:** React 18.2
- **Build Tool:** Vite 8.0
- **Linguagem:** TypeScript 5.3
- **Styling:** Tailwind CSS 3.3
- **HTTP Client:** Axios 1.6
- **Router:** React Router 6.17

### Backend
- **Framework:** FastAPI 0.104
- **Server:** Uvicorn 0.24
- **ORM:** SQLAlchemy 2.0
- **Database:** PostgreSQL 15
- **IA:** Anthropic Claude API
- **Auth:** Python-Jose + Bcrypt
- **Validation:** Pydantic 2.5

### DevOps
- **Database (Local):** PostgreSQL via Docker
- **Frontend Deploy:** Vercel
- **Backend Deploy:** Render
- **Version Control:** Git

---

## 🏗 Arquitetura

```
┌─────────────────────────────────────────────────────┐
│ Frontend (React + Vite)                             │
│ http://localhost:5173                               │
│ - ChatInput (busca)                                 │
│ - PrestadorCard (resultado)                         │
│ - Responsive Design (Tailwind)                      │
└─────────────┬───────────────────────────────────────┘
              │ HTTP/REST
              │ CORS habilitado
              ▼
┌─────────────────────────────────────────────────────┐
│ Backend (FastAPI)                                   │
│ http://localhost:8000                               │
│ - Chat Service (Claude AI)                          │
│ - CRUD Prestadores/Feedback                         │
│ - Ranking Service (Score)                           │
│ - Auth (Token simples)                              │
└─────────────┬───────────────────────────────────────┘
              │ SQL
              │ Connection Pool
              ▼
┌─────────────────────────────────────────────────────┐
│ Database (PostgreSQL)                               │
│ localhost:5432                                      │
│ - Tabelas: categorias, condominios, prestadores,   │
│   feedback, usuarios                                │
└─────────────────────────────────────────────────────┘
```

---

## 📦 Componentes

### Frontend

#### `src/components/ChatInput.tsx`
- Form de input para busca
- Estados: `input` (string), `isLoading` (boolean)
- Props: `onSend` (callback), `isLoading` (boolean)
- Estilos: Tailwind (input + button)

#### `src/components/PrestadorCard.tsx`
- Exibe um prestador com score
- Props: `prestador` (Prestador interface)
- Mostra: nome, score (0-10), link WhatsApp
- Estilos: border, hover effects, badges

#### `src/App.tsx`
- Componente raiz
- Estado: `results` (Prestador[]), `isLoading`, `pergunta`
- Fetch para `/api/chat/buscar`
- Renderiza ChatInput + PrestadorCards

### Backend

#### Routes

**POST `/api/chat/buscar`**
- Request: `{ pergunta: string }`
- Response: `{ pergunta, categoria, condominio, prestadores[], total_resultados }`
- Logic:
  1. Extrai categoria/condominio com Claude
  2. Busca prestadores por categoria
  3. Calcula score de cada um
  4. Retorna ordenado por score DESC

**GET `/api/prestadores`**
- Query params: `categoria_id`, `condominio_id`, `status_filter`
- Response: `Prestador[]`

**POST `/api/prestadores`**
- Headers: `Authorization: token`
- Body: nome, whatsapp, categoria_id, condominio_ids[], notas
- Response: Prestador criado

**POST `/api/feedback`**
- Headers: `Authorization: token`
- Body: prestador_id, condominio_id, categoria_id, qualidade (1-5), material_estimativa, prazo_manteve, custo_manteve, observacoes
- Response: Feedback criado

**GET `/api/feedback/stats/:prestador_id`**
- Query: `condominio_id` (opcional)
- Response: FeedbackStats (score_final, material_acertou_pct, etc)

**GET `/health`**
- Response: `{ status: "ok", version: "0.1.0" }`

#### Services

**`chat_service.py`**
```python
extrair_categoria_e_condominio(pergunta, db)
  # Usa Claude para NLP
  # Fallback: retorna primeiro categoria/condominio
  # Returns: (categoria_id, condominio_id)

buscar_prestadores(categoria_id, condominio_id, db)
  # Query SQL com joins
  # Calcula score via ranking_service
  # Returns: Prestador[] ordenado por score DESC
```

**`ranking_service.py`**
```python
calcular_stats_prestador(prestador_id, condominio_id, db)
  # Busca feedbacks do prestador
  # Calcula:
  #   - material_acertou_pct
  #   - prazo_cumprido_pct
  #   - custo_mantido_pct
  #   - qualidade_media
  #   - score_final = (M*2) + (P*1.5) + (C*1.5) + Q
  # Returns: FeedbackStats
```

#### Models (SQLAlchemy)

```python
Categoria
  - id, nome, descricao

Condominio
  - id, nome, cidade, criado_em

Prestador
  - id, nome, whatsapp, categoria_id, condominio_ids (ARRAY), status, notas, criado_em

Feedback
  - id, prestador_id, condominio_id, categoria_id, data_feedback
  - qualidade (1-5), material_estimativa, prazo_manteve, custo_manteve
  - observacoes, seu_feedback, criado_em

Usuario
  - id, email, senha_hash, nome, criado_em, ativo
```

---

## 🔌 APIs

### Endpoints Completos

| Método | Endpoint | Auth | Descrição |
|--------|----------|------|-----------|
| POST | `/api/chat/buscar` | ❌ | Busca com IA |
| GET | `/api/prestadores` | ❌ | Lista prestadores |
| POST | `/api/prestadores` | ✅ | Criar prestador |
| PUT | `/api/prestadores/{id}` | ✅ | Atualizar |
| DELETE | `/api/prestadores/{id}` | ✅ | Deletar |
| GET | `/api/categorias` | ❌ | Lista categorias |
| POST | `/api/categorias` | ✅ | Criar categoria |
| GET | `/api/condominios` | ❌ | Lista condomínios |
| POST | `/api/condominios` | ✅ | Criar condomínio |
| GET | `/api/feedback` | ❌ | Lista feedback |
| POST | `/api/feedback` | ✅ | Criar feedback |
| GET | `/api/feedback/stats/{id}` | ❌ | Stats de prestador |
| GET | `/health` | ❌ | Health check |

### Exemplo de Busca

```bash
curl -X POST http://localhost:8000/api/chat/buscar \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "Preciso de um encanador em Vargem Grande"}'
```

Response:
```json
{
  "pergunta": "Preciso de um encanador em Vargem Grande",
  "categoria": "Encanaria",
  "condominio": "Vargem Grande",
  "prestadores": [
    {
      "id": 1,
      "nome": "João Silva",
      "whatsapp": "11999887766",
      "link_whatsapp": "https://wa.me/5511999887766?text=...",
      "score_final": 8.5,
      "feedback_count": 5,
      "qualidade_media": 4.8,
      "material_acertou_pct": 1.0,
      "prazo_cumprido_pct": 1.0,
      "custo_mantido_pct": 0.8
    }
  ],
  "total_resultados": 1
}
```

---

## 🚀 Setup Local

### Pré-requisitos
- Python 3.9+
- Node.js 20+
- Docker (para PostgreSQL)
- Git

### Passo 1: PostgreSQL

```bash
docker run --name chatvgp-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=chatvgp \
  -p 5432:5432 -d postgres:15
```

### Passo 2: Backend

```bash
cd chatvgp/backend

# Virtual env
python3 -m venv venv
source venv/bin/activate

# Dependências
pip install -r requirements.txt

# .env
cat > .env << 'EOF'
DATABASE_URL=postgresql://postgres:password@localhost:5432/chatvgp
SECRET_KEY=dev-secret-key-change-in-production
CLAUDE_API_KEY=sk-your-actual-key-here
ENVIRONMENT=development
DEBUG=True
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
EOF

# Rodar
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Passo 3: Frontend

```bash
cd frontend-vite

# Dependências
npm install

# .env
cat > .env << 'EOF'
VITE_API_BASE_URL=http://localhost:8000/api
EOF

# Rodar
npm run dev
```

### Passo 4: Criar dados

Acessa http://localhost:8000/docs (Swagger) e cria:
1. Categoria (Encanaria)
2. Condominio (Vargem Grande)
3. Prestador (João Silva)
4. Feedback (qualidade 5, material ok, prazo ok)

---

## 📤 Deploy

### Backend (Render)

1. Preparar:
```bash
# Adiciona ao requirements.txt
gunicorn==21.2.0
python-multipart==0.0.6

# Cria Procfile
web: gunicorn -w 4 -b 0.0.0.0:$PORT app.main:app --worker-class uvicorn.workers.UvicornWorker
```

2. Render Dashboard:
- New Web Service
- Conecta GitHub repo
- Root directory: `chatvgp/backend`
- Build: `pip install -r requirements.txt`
- Start: `gunicorn ...`
- Add variables: DATABASE_URL, CLAUDE_API_KEY, SECRET_KEY
- Deploy

3. Result: `https://chatvgp-api.onrender.com`

### Frontend (Vercel)

1. Update `.env`:
```
VITE_API_BASE_URL=https://chatvgp-api.onrender.com/api
```

2. Vercel:
- Add Project
- Select GitHub repo
- Root: `chatvgp/frontend`
- Framework: Create React App
- Deploy

3. Result: `https://chatvgp.vercel.app`

---

## 🔧 Troubleshooting

### "Port 8000 already in use"
```bash
lsof -i :8000
kill -9 <PID>
# Ou usa porta diferente
python3 -m uvicorn app.main:app --port 8001
```

### "Cannot connect to database"
```bash
# Verifica se PostgreSQL está rodando
docker ps | grep chatvgp-db

# Se não, inicia
docker start chatvgp-db
```

### "CORS error"
- Verifica CORS_ORIGINS no .env
- Frontend URL deve estar na lista
- Reinicia backend

### "Claude API error"
- Se CLAUDE_API_KEY=sk-placeholder, sistema usa fallback (primeira categoria/condomínio)
- Para IA completa, precisa chave real de `https://console.anthropic.com`

### Frontend mostra "Backend offline"
- Verifica se backend está rodando: `curl http://localhost:8000/health`
- Verifica se VITE_API_BASE_URL está correto em `.env`

---

## 📈 Metrics & Monitoring

### Performance
- Frontend: Vite ~150ms startup
- Backend: FastAPI ~100ms response
- Database: PostgreSQL queries <100ms

### Observability
- Backend logs via Uvicorn
- Frontend console via DevTools
- Swagger docs: `http://localhost:8000/docs`

### Segurança Atual
- ✅ CORS configurado
- ✅ Validação Pydantic
- ✅ SQL injection prevention (SQLAlchemy)
- ⏳ JWT authentication (pronto, não ativado)
- ⏳ Rate limiting (ready)

---

## 🎯 Roadmap

### Curto Prazo (2 semanas)
- [ ] JWT authentication completo
- [ ] Admin panel com feedback management
- [ ] Rating público (5 stars)
- [ ] Mobile responsividade refinada

### Médio Prazo (1-2 meses)
- [ ] Dashboard de estatísticas
- [ ] Filtros avançados (rating, experiência)
- [ ] Email notifications
- [ ] Testes unitários

### Longo Prazo (3+ meses)
- [ ] App mobile (React Native)
- [ ] Payment system (Stripe)
- [ ] SMS notifications
- [ ] Advanced analytics
- [ ] SEO otimizado

---

## 📞 Contato & Suporte

**Repositório:** GitHub  
**Issues:** GitHub Issues  
**Documentação:** Este arquivo + arquivos .md na raiz

**Ambiente de Desenvolvimento:**
- Terminal 1: PostgreSQL (Docker)
- Terminal 2: Backend (Uvicorn)
- Terminal 3: Frontend (Vite)

---

**Última atualização:** Junho 2, 2026  
**Versão do documento:** 1.0.0
