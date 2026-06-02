# ChatVGP - Setup do Ambiente

## Backend Setup (FastAPI + PostgreSQL)

### 1. Clonar/Configurar Repositório
```bash
cd chatvgp/backend
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 2. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente
```bash
cp .env.example .env
# Editar .env com seus valores:
# DATABASE_URL=postgresql://user:password@localhost:5432/chatvgp
# SECRET_KEY=seu-secret-muito-seguro-aqui
# CLAUDE_API_KEY=sk-xxx
```

### 4. Setup do PostgreSQL

**Opção A: PostgreSQL Local**
```bash
# Instalar PostgreSQL (macOS)
brew install postgresql
brew services start postgresql

# Criar banco
createdb chatvgp
```

**Opção B: PostgreSQL via Docker**
```bash
docker run --name chatvgp-db -e POSTGRES_PASSWORD=password -e POSTGRES_DB=chatvgp -p 5432:5432 -d postgres:15
```

### 5. Rodar Servidor
```bash
cd chatvgp/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Acesse: http://localhost:8000/docs (Swagger UI)

---

## Frontend Setup (React + TypeScript)

### 1. Criar Projeto React
```bash
cd chatvgp
npx create-react-app frontend --template typescript
cd frontend
```

### 2. Instalar Dependências Adicionais
```bash
npm install axios react-router-dom
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### 3. Configurar API Base URL
Criar `.env` no frontend:
```
REACT_APP_API_BASE_URL=http://localhost:8000/api
```

### 4. Rodar Frontend
```bash
npm start
```

Acessa: http://localhost:3000

---

## Deploy (Produção)

### Backend em Render.com
1. Fazer push no GitHub
2. Conectar repo no Render
3. Criar PostgreSQL database em Render
4. Definir variáveis de ambiente no Render
5. Deploy automático

### Frontend em Vercel
1. Push no GitHub
2. Conectar em Vercel
3. Deploy automático

---

## Próximas Tarefas

- [ ] Completar rotas de Prestadores (CRUD)
- [ ] Completar rotas de Feedback
- [ ] Completar rotas de Admin
- [ ] Autenticação (Login/Register)
- [ ] Frontend do Chat
- [ ] Frontend do Admin Panel
- [ ] Testes unitários
- [ ] Documentação API
