# ChatVGP - AI-Powered Service Provider Discovery

Plataforma de busca de prestadores de serviços por inteligência artificial natural.

## 🏗️ Arquitetura

```
Frontend (React + Vite)          Backend (FastAPI)              Database (PostgreSQL)
├── Vercel                       ├── Render                     ├── Render
├── TypeScript                   ├── Python 3.11                └── SQLAlchemy ORM
├── Tailwind CSS                 ├── Uvicorn + Gunicorn
└── Vite                         └── SQLAlchemy
```

## 🚀 URLs de Produção

- **Frontend:** https://chatvgp.vercel.app
- **Backend API:** https://chatvgp-api.onrender.com
- **Documentação:** https://chatvgp-api.onrender.com/docs

## 📋 Endpoints da API

### Chat - Busca de Prestadores

```bash
POST /api/chat/buscar
Content-Type: application/json

{
  "pergunta": "preciso de um encanador"
}
```

**Resposta:**
```json
{
  "pergunta": "preciso de um encanador",
  "categoria": "Encanador",
  "condominio": "Haras Bela Vista",
  "prestadores": [
    {
      "id": 1,
      "nome": "Carlos Silva",
      "whatsapp": "11987654321",
      "link_whatsapp": "https://wa.me/...",
      "score_final": 4.5,
      "feedback_count": 10,
      "qualidade_media": 4.5,
      "material_acertou_pct": 0.8,
      "prazo_cumprido_pct": 0.9,
      "custo_mantido_pct": 0.7
    }
  ],
  "total_resultados": 1
}
```

### Autenticação - Login

```bash
POST /api/auth/login
Content-Type: application/json

{
  "senha": "dev-secret-key"
}
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in_days": 7
}
```

### Prestadores - CRUD

**Listar (GET):**
```bash
GET /api/prestadores?categoria_id=1&status=ativo
```

**Criar (POST):**
```bash
POST /api/prestadores
Authorization: Bearer <token>
Content-Type: application/json

{
  "nome": "João Silva",
  "whatsapp": "11987654321",
  "categoria_id": 1,
  "condominio_ids": [1],
  "status": "ativo"
}
```

**Atualizar (PUT):**
```bash
PUT /api/prestadores/1
Authorization: Bearer <token>
Content-Type: application/json

{
  "nome": "João Silva Atualizado",
  "status": "inativo"
}
```

**Deletar (DELETE):**
```bash
DELETE /api/prestadores/1
Authorization: Bearer <token>
```

### Feedback - CRUD

**Criar (POST):**
```bash
POST /api/feedback
Authorization: Bearer <token>
Content-Type: application/json

{
  "prestador_id": 1,
  "condominio_id": 1,
  "categoria_id": 1,
  "data_feedback": "2026-06-02",
  "qualidade": 5,
  "material_estimativa": "Acertou",
  "prazo_manteve": true,
  "custo_manteve": true,
  "observacoes": "Excelente trabalho!",
  "seu_feedback": false
}
```

### Categorias

```bash
GET /api/categorias
POST /api/categorias (requer autenticação)
```

### Condomínios

```bash
GET /api/condominios
POST /api/condominios (requer autenticação)
```

### Health Check

```bash
GET /health
```

## 🔐 Autenticação

Endpoints de escrita (POST, PUT, DELETE) requerem JWT token:

```bash
curl -X POST https://chatvgp-api.onrender.com/api/prestadores \
  -H "Authorization: Bearer <seu_token>" \
  -H "Content-Type: application/json" \
  -d '{"nome": "João", "whatsapp": "11987654321", "categoria_id": 1, "condominio_ids": [1], "status": "ativo"}'
```

**Como obter token:**

1. Chamar `/api/auth/login` com a senha (padrão: `dev-secret-key`)
2. Guardar o `access_token` retornado
3. Usar no header `Authorization: Bearer <token>` em requisições protegidas

Token expira em **7 dias**.

## 🗂️ Estrutura do Projeto

```
chatvgp/
├── backend/
│   ├── app/
│   │   ├── routes/           # Endpoints da API
│   │   │   ├── auth.py       # Login e tokens JWT
│   │   │   ├── chat.py       # Busca de prestadores
│   │   │   ├── prestadores.py
│   │   │   ├── feedback.py
│   │   │   ├── categorias.py
│   │   │   └── condominios.py
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic validation
│   │   ├── services/         # Business logic
│   │   ├── config.py         # Environment variables
│   │   ├── database.py       # DB connection
│   │   └── main.py           # FastAPI app
│   ├── requirements-render.txt
│   ├── Dockerfile
│   └── runtime.txt
├── chatvgp/frontend/
│   ├── src/
│   │   ├── pages/             # ChatPage, IndicarProfissional, etc.
│   │   └── App.jsx
│   ├── .env.example           # Environment variables
│   └── package.json
└── README.md
```

## 🔧 Variáveis de Ambiente

### Backend (Render)

```
DATABASE_URL=postgresql://user:pass@host/chatvgp
SECRET_KEY=seu-secret-key-jwt
CLAUDE_API_KEY=sk-ant-... (opcional - usar keyword matching se vazio)
ENVIRONMENT=production
DEBUG=False
CORS_ORIGINS=https://chatvgp.vercel.app,https://chatvgp.com
```

### Frontend (Vercel)

```
REACT_APP_API_BASE_URL=https://chatvgp-api.onrender.com/api
```

## 📊 Modelos de Dados

### Prestador
- `id`: Integer (PK)
- `nome`: String (indexed)
- `whatsapp`: String
- `categoria_id`: Integer (FK)
- `condominio_ids`: Array[Integer]
- `status`: String (ativo/inativo)
- `notas`: String
- `criado_em`: DateTime

### Feedback
- `id`: Integer (PK)
- `prestador_id`: Integer (FK)
- `condominio_id`: Integer (FK)
- `categoria_id`: Integer (FK)
- `qualidade`: Integer (1-5)
- `material_estimativa`: String
- `prazo_manteve`: Boolean
- `custo_manteve`: Boolean
- `observacoes`: String
- `seu_feedback`: Boolean
- `data_feedback`: Date
- `criado_em`: DateTime

### Categoria
- `id`: Integer (PK)
- `nome`: String (unique)
- `criado_em`: DateTime

### Condominio
- `id`: Integer (PK)
- `nome`: String
- `cidade`: String
- `criado_em`: DateTime

## 🧪 Testes

### Buscar prestador de encanador
```bash
curl -X POST https://chatvgp-api.onrender.com/api/chat/buscar \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "preciso de um encanador"}'
```

### Buscar prestador de desenvolvedor
```bash
curl -X POST https://chatvgp-api.onrender.com/api/chat/buscar \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "preciso de um desenvolvedor"}'
```

### Listar todos os prestadores
```bash
curl https://chatvgp-api.onrender.com/api/prestadores
```

### Fazer login e obter token
```bash
curl -X POST https://chatvgp-api.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"senha": "dev-secret-key"}'
```

## 🚀 Deploy

### Backend (Render)
1. Conectar repositório GitHub
2. Build command: `pip install -r requirements-render.txt`
3. Start command: `gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:10000`
4. Environment variables: DATABASE_URL, SECRET_KEY, etc.

### Frontend (Vercel)
1. Conectar repositório GitHub
2. Framework: Vite
3. Build output: `dist`
4. Environment variables: VITE_API_BASE_URL

## 📝 Notas

- **Keyword Matching:** Categorias e condomínios são identificados por palavras-chave na pergunta
- **JWT:** Tokens válidos por 7 dias
- **CORS:** Configurado para aceitar requisições do frontend
- **Feedback:** Score final é calculado baseado em qualidade, material estimativa, prazo e custo

## 📧 Contato

hurbem@gmail.com
