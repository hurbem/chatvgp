# ChatVGP — Arquitetura do MVP

## 1. Estrutura de Pastas

```
chatvgp/
├── backend/                    # FastAPI + Python
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # Entry point
│   │   ├── config.py          # Configurações (DB, segurança)
│   │   ├── database.py        # Conexão PostgreSQL
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── prestador.py
│   │   │   ├── categoria.py
│   │   │   ├── condominio.py
│   │   │   ├── feedback.py
│   │   │   └── usuario.py
│   │   ├── schemas/           # Pydantic schemas (validação)
│   │   │   ├── __init__.py
│   │   │   ├── prestador.py
│   │   │   ├── feedback.py
│   │   │   └── chat.py
│   │   ├── routes/            # Endpoints da API
│   │   │   ├── __init__.py
│   │   │   ├── auth.py        # Login/registro admin
│   │   │   ├── prestadores.py
│   │   │   ├── feedback.py
│   │   │   ├── chat.py        # Busca de prestadores
│   │   │   ├── ranking.py
│   │   │   └── admin.py       # Painel admin
│   │   ├── services/          # Lógica de negócio
│   │   │   ├── __init__.py
│   │   │   ├── ranking_service.py    # Cálculo de ranking
│   │   │   ├── chat_service.py       # Lógica do chat
│   │   │   └── ai_service.py         # Integração IA (Claude)
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── security.py    # Hashing, JWT
│   │       └── logger.py
│   ├── requirements.txt
│   ├── .env.example
│   └── main.py                # Script de execução

├── frontend/                   # React + TypeScript
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat/
│   │   │   │   ├── ChatWindow.tsx
│   │   │   │   ├── ChatInput.tsx
│   │   │   │   └── ChatResult.tsx
│   │   │   ├── Admin/
│   │   │   │   ├── PrestadorList.tsx
│   │   │   │   ├── PrestadorForm.tsx
│   │   │   │   ├── FeedbackPanel.tsx
│   │   │   │   └── RankingView.tsx
│   │   │   ├── Navigation.tsx
│   │   │   └── Layout.tsx
│   │   ├── pages/
│   │   │   ├── ChatPage.tsx
│   │   │   ├── AdminPage.tsx
│   │   │   ├── LoginPage.tsx
│   │   │   └── NotFoundPage.tsx
│   │   ├── services/
│   │   │   ├── api.ts         # Chamadas HTTP
│   │   │   └── auth.ts        # Autenticação
│   │   ├── types/
│   │   │   ├── index.ts       # TypeScript types
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── package.json
│   └── .env.example

└── docs/
    ├── API.md
    ├── SETUP.md
    └── DEPLOY.md
```

---

## 2. Modelos de Dados (Database Schema)

### Tabela: usuarios
```sql
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    nome VARCHAR(255),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT TRUE
);
```

### Tabela: categorias
```sql
CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) UNIQUE NOT NULL,
    descricao TEXT
);
```

### Tabela: condominios
```sql
CREATE TABLE condominios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabela: prestadores
```sql
CREATE TABLE prestadores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    whatsapp VARCHAR(20) NOT NULL,
    categoria_id INTEGER REFERENCES categorias(id),
    condominios_ids INTEGER[] (array de IDs),
    status VARCHAR(20) DEFAULT 'ativo', -- 'ativo', 'inativo'
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notas TEXT
);
```

### Tabela: feedbacks
```sql
CREATE TABLE feedbacks (
    id SERIAL PRIMARY KEY,
    prestador_id INTEGER REFERENCES prestadores(id),
    condominio_id INTEGER REFERENCES condominios(id),
    categoria_id INTEGER REFERENCES categorias(id),
    data_feedback DATE,
    qualidade INTEGER CHECK (qualidade >= 1 AND qualidade <= 5),
    material_estimativa VARCHAR(50), -- 'Acertou', 'Subestimou 10-25%', etc
    prazo_manteve BOOLEAN,
    custo_manteve BOOLEAN,
    observacoes TEXT,
    seu_feedback BOOLEAN DEFAULT FALSE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. Endpoints da API (FastAPI)

### Auth
- `POST /api/auth/login` — Login admin
- `POST /api/auth/register` — Registro (apenas admin, primeira vez)
- `GET /api/auth/me` — Dados do usuário logado

### Prestadores
- `GET /api/prestadores` — Listar todos
- `GET /api/prestadores/{id}` — Detalhes
- `POST /api/prestadores` — Criar (admin only)
- `PUT /api/prestadores/{id}` — Editar (admin only)
- `DELETE /api/prestadores/{id}` — Deletar (admin only)

### Categorias
- `GET /api/categorias` — Listar
- `POST /api/categorias` — Criar (admin only)

### Condomínios
- `GET /api/condominios` — Listar
- `POST /api/condominios` — Criar (admin only)

### Feedback
- `POST /api/feedback` — Registrar novo feedback (admin only)
- `GET /api/feedback/{prestador_id}` — Feedbacks de um prestador
- `GET /api/feedback/stats/{prestador_id}` — Stats agregadas

### Chat (Busca de Prestadores)
- `POST /api/chat/buscar` — Enviar pergunta
  - Input: `{ pergunta: string, condominio_id?: int }`
  - Output: `{ prestadores: [{ nome, whatsapp, link_whatsapp, score, feedback_count }] }`

### Ranking
- `GET /api/ranking/por-condominio/{condominio_id}` — Ranking de um condomínio
- `GET /api/ranking/prestador/{prestador_id}` — Score detalhado de um prestador

### Admin
- `GET /api/admin/dashboard` — Dados gerais (total prestadores, feedbacks, etc)
- `GET /api/admin/prestadores-sem-feedback` — Prestadores que precisam de feedback

---

## 4. Fluxo do Chat (Core do MVP)

**Cliente faz pergunta:**
```
Input: "Preciso de um encanador em Vargem Grande Paulista"
```

**Processamento (backend):**
1. Parse da pergunta (NLP básico ou regex)
   - Extrai categoria: "encanador" → categoria_id = 1
   - Extrai cidade/condomínio se mencionado
2. Busca no banco
   ```sql
   SELECT p.*, 
          AVG(f.qualidade) as nota_media,
          ROUND((SUM(CASE WHEN f.material_estimativa = 'Acertou' THEN 1 ELSE 0 END) / COUNT(*) * 100), 0) as material_acertou_pct,
          ...
   FROM prestadores p
   LEFT JOIN feedbacks f ON p.id = f.prestador_id
   WHERE p.categoria_id = 1 
     AND p.status = 'ativo'
   GROUP BY p.id
   ORDER BY score_final DESC
   LIMIT 5
   ```
3. Calcula Score Final (como no Excel)
4. Retorna top 5 prestadores

**Output:**
```json
{
  "pergunta": "Preciso de um encanador em Vargem Grande Paulista",
  "categoria": "Encanaria",
  "prestadores": [
    {
      "id": 1,
      "nome": "João Silva",
      "whatsapp": "11999887766",
      "link_whatsapp": "https://wa.me/5511999887766?text=...",
      "score_final": 8.5,
      "feedback_count": 3,
      "qualidade_media": 4.7,
      "material_acertou_pct": 100,
      "prazo_cumprido_pct": 100,
      "custo_mantido_pct": 100
    },
    ...
  ]
}
```

---

## 5. Componentes Frontend (React)

### Página: Chat Público
- Input de texto livre ("Preciso de...")
- Lista de resultados com:
  - Nome do prestador
  - Score visual (⭐⭐⭐⭐⭐ ou barra de progresso)
  - Botão "Contatar via WhatsApp" (abre mensagem padrão)

### Página: Admin (Protegida por Login)

**Seção 1: Prestadores**
- Tabela: listar todos
- Botão: Adicionar novo
- Formulário: Nome, WhatsApp, Categoria, Condomínios, Status
- Ações: Editar, Deletar, Ver Feedbacks

**Seção 2: Feedback**
- Formulário: Prestador, Condomínio, Qualidade (1-5), Material (dropdown), Prazo, Custo, Observações
- Histórico: Listar feedbacks por prestador

**Seção 3: Ranking**
- Tabela: Prestador, Categoria, Condomínio, Score, Posição
- Filtros: Por condomínio, por categoria
- Detalhes: Clica num prestador, vê breakdown (qual % acertou material, etc)

**Seção 4: Dashboard**
- Cards: Total prestadores, total feedbacks coletados, prestadores mais bem rankeados
- Gráfico: Feedback por semana

---

## 6. Segurança (Checklist)

- [ ] Senha admin com hash (bcrypt)
- [ ] JWT tokens para sessão (não cookies simples)
- [ ] HTTPS obrigatório (Render/Railway fazem automático)
- [ ] CORS restrito (apenas frontend)
- [ ] SQL injection previsto (SQLAlchemy parameterizado)
- [ ] Rate limiting em endpoints sensíveis (login, chat)
- [ ] Validação Pydantic em todos os inputs
- [ ] Variáveis de ambiente (.env, não commitadas)
- [ ] Logs de auditoria (quem criou/editou prestador)

---

## 7. Timeline MVP (Estimativa)

| Fase | Duração | O quê |
|------|---------|-------|
| Setup + Auth | 2-3 dias | Projeto, DB, login admin |
| CRUD Prestadores | 2 dias | Criar/editar/deletar prestadores |
| Feedback | 2 dias | Form de feedback, salvar no DB |
| Chat API | 2 dias | Lógica de busca, ranking |
| Frontend Chat | 3 dias | Interface do chat público |
| Frontend Admin | 3 dias | Painel admin |
| Testes + Deploy | 2 dias | Validação, Render/Railway |
| **Total** | **~2 semanas** | MVP funcionando |

---

## 8. Próximas Decidir

1. **Banco de dados**: PostgreSQL (recomendado) ou SQLite pra começar (mais simples)?
2. **IA para NLP**: Usar Claude API para entender perguntas ou regex/keywords?
3. **Autenticação**: Apenas admin (email/senha) ou clientes também?
4. **WhatsApp link**: Mensagem padrão é "Olá encontrei sua recomendação no chatVGP, estou precisando falar contigo" ou personalizar?

---

Faz sentido? Quer que comece direto no setup do projeto ou ajusta algo na arquitetura primeiro?
