# ChatVGP - Setup Completo (Backend + Frontend)

## Pré-requisitos

- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Docker (opcional, para PostgreSQL)

---

## Backend Setup (FastAPI)

### 1. Criar estrutura e virtual env
```bash
cd chatvgp/backend
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente
```bash
cp .env.example .env
```

**Editar `.env`:**
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/chatvgp
SECRET_KEY=seu-secret-key-mude-em-producao
CLAUDE_API_KEY=sk-your-api-key-here
CORS_ORIGINS=["http://localhost:3000"]
```

### 4. Setup do PostgreSQL

**Opção A: PostgreSQL Local (macOS com Homebrew)**
```bash
brew install postgresql
brew services start postgresql
createdb chatvgp
```

**Opção B: PostgreSQL via Docker**
```bash
docker run --name chatvgp-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=chatvgp \
  -p 5432:5432 \
  -d postgres:15
```

### 5. Rodar servidor FastAPI
```bash
cd chatvgp/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Teste:**
```bash
curl http://localhost:8000/health
# Resposta: {"status":"ok","version":"0.1.0"}
```

**Documentação interativa:** `http://localhost:8000/docs`

---

## Frontend Setup (React)

### 1. Instalar dependências
```bash
cd chatvgp/frontend
npm install
```

### 2. Configurar variáveis de ambiente
```bash
cp .env.example .env
```

**.env já vem configurado corretamente:**
```
REACT_APP_API_BASE_URL=http://localhost:8000/api
```

### 3. Rodar servidor de desenvolvimento
```bash
npm start
```

**Acesso:** `http://localhost:3000`

---

## Teste Completo

### 1. Criar dados iniciais

**Via Swagger (`http://localhost:8000/docs`):**

Ou via curl:

```bash
# Criar categoria
curl -X POST http://localhost:8000/api/categorias \
  -H "Authorization: token" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Encanaria", "descricao": "Serviços hidráulicos"}'

# Criar condomínio
curl -X POST http://localhost:8000/api/condominios \
  -H "Authorization: token" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Condomínio A", "cidade": "Vargem Grande Paulista"}'

# Criar prestador
curl -X POST http://localhost:8000/api/prestadores \
  -H "Authorization: token" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "whatsapp": "11999887766",
    "categoria_id": 1,
    "condominio_ids": [1],
    "status": "ativo"
  }'

# Criar feedback
curl -X POST http://localhost:8000/api/feedback \
  -H "Authorization: token" \
  -H "Content-Type: application/json" \
  -d '{
    "prestador_id": 1,
    "condominio_id": 1,
    "categoria_id": 1,
    "data_feedback": "2026-02-15",
    "qualidade": 5,
    "material_estimativa": "Acertou",
    "prazo_manteve": true,
    "custo_manteve": true,
    "seu_feedback": true
  }'
```

### 2. Testar no Frontend

1. Acesse `http://localhost:3000`
2. Digite: "Preciso de um encanador"
3. Veja o prestador retornado com score

### 3. Acessar Admin

1. Clique em "🔐 Admin" (botão flutuante)
2. Token: `admin-token` (qualquer valor não-vazio funciona)
3. Veja a aba "Prestadores" com lista de cadastrados
4. Cadastre novos prestadores no formulário

---

## Estrutura do Projeto

```
chatvgp/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Configurações
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models/              # DB models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── routes/              # API endpoints
│   │   ├── services/            # Lógica de negócio
│   │   └── utils/               # Utilidades
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
└── frontend/
    ├── src/
    │   ├── components/          # React components
    │   ├── pages/               # Pages (Chat, Admin)
    │   ├── services/            # API client
    │   ├── types/               # TypeScript types
    │   ├── App.tsx              # Root component
    │   └── index.tsx            # Entry point
    ├── public/
    │   └── index.html
    ├── package.json
    ├── tailwind.config.js
    ├── .env.example
    └── README.md
```

---

## Endpoints Disponíveis

### Chat (Público)
- `POST /api/chat/buscar` — Buscar prestadores por pergunta

### Prestadores
- `GET /api/prestadores` — Listar com scores
- `GET /api/prestadores/{id}` — Detalhe
- `POST /api/prestadores` — Criar (admin)
- `PUT /api/prestadores/{id}` — Editar (admin)
- `DELETE /api/prestadores/{id}` — Deletar (admin)

### Feedback
- `GET /api/feedback` — Listar
- `GET /api/feedback/stats/{id}` — Stats com score
- `POST /api/feedback` — Criar (admin)
- `GET /api/feedback/ranking/por-condominio/{id}` — Ranking

### Categorias & Condomínios
- `GET/POST /api/categorias` — Gerenciar categorias
- `GET/POST /api/condominios` — Gerenciar condomínios

---

## Troubleshooting

### Backend não conecta ao banco
```bash
# Verificar se PostgreSQL tá rodando
psql -U postgres -d chatvgp

# Se banco não existe
createdb chatvgp

# Revisar DATABASE_URL no .env
```

### Frontend não consegue falar com backend
```bash
# Verificar se backend tá rodando
curl http://localhost:8000/health

# Verificar CORS em .env do backend
CORS_ORIGINS=["http://localhost:3000"]

# No frontend, verificar .env
REACT_APP_API_BASE_URL=http://localhost:8000/api
```

### Erro 401 no Admin
```bash
# Qualquer valor não-vazio funciona como token
# Use: "admin-token", "token", "123", etc.
```

---

## Próximas Tarefas

- [ ] Autenticação com JWT (atualmente usa token simples)
- [ ] Testes unitários (backend + frontend)
- [ ] Deploy (Backend em Render, Frontend em Vercel)
- [ ] Aba de feedback completa no admin
- [ ] Aba de ranking completa no admin
- [ ] Mobile responsividade
- [ ] Dark mode

---

## Documentação Adicional

- `API-ENDPOINTS.md` — Detalhes de todos os endpoints
- `TESTE-RAPIDO.md` — Commands prontos para copiar/colar
- `chatvgp/backend/README.md` — Setup backend detalhado
- `chatvgp/frontend/README.md` — Setup frontend detalhado
