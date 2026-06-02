# ChatVGP — Teste Rápido da API

## Pré-requisitos

```bash
# Instalar e rodar server
cd chatvgp/backend
pip install -r requirements.txt
cp .env.example .env
# Editar .env com DATABASE_URL e CLAUDE_API_KEY

# Rodar PostgreSQL (Docker)
docker run --name chatvgp-db -e POSTGRES_PASSWORD=password -e POSTGRES_DB=chatvgp -p 5432:5432 -d postgres:15

# Rodar servidor
uvicorn app.main:app --reload
```

Acesso: `http://localhost:8000/docs` (Swagger UI)

---

## Teste Manual (Curl)

### 1. Criar Categorias
```bash
# Encanaria
curl -X POST http://localhost:8000/api/categorias \
  -H "Authorization: token" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Encanaria", "descricao": "Serviços hidráulicos"}'

# Eletricista
curl -X POST http://localhost:8000/api/categorias \
  -H "Authorization: token" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Eletricista", "descricao": "Instalação elétrica"}'

# Limpeza
curl -X POST http://localhost:8000/api/categorias \
  -H "Authorization: token" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Limpeza", "descricao": "Limpeza residencial"}'
```

### 2. Criar Condomínios
```bash
# Vargem Grande Paulista - A
curl -X POST http://localhost:8000/api/condominios \
  -H "Authorization: token" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Condomínio A", "cidade": "Vargem Grande Paulista"}'

# Vargem Grande Paulista - B
curl -X POST http://localhost:8000/api/condominios \
  -H "Authorization: token" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Condomínio B", "cidade": "Vargem Grande Paulista"}'

# Cotia - C
curl -X POST http://localhost:8000/api/condominios \
  -H "Authorization: token" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Condomínio C", "cidade": "Cotia"}'
```

### 3. Criar Prestadores
```bash
# João Silva - Encanaria
curl -X POST http://localhost:8000/api/prestadores \
  -H "Authorization: token" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "whatsapp": "11999887766",
    "categoria_id": 1,
    "condominio_ids": [1, 2],
    "status": "ativo",
    "notas": "Excelente encanador"
  }'

# Maria Santos - Eletricista
curl -X POST http://localhost:8000/api/prestadores \
  -H "Authorization: token" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria Santos",
    "whatsapp": "11988776655",
    "categoria_id": 2,
    "condominio_ids": [1, 3],
    "status": "ativo",
    "notas": "Eletricista com 10 anos de experiência"
  }'

# Carlos Oliveira - Limpeza
curl -X POST http://localhost:8000/api/prestadores \
  -H "Authorization: token" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Carlos Oliveira",
    "whatsapp": "11977665544",
    "categoria_id": 3,
    "condominio_ids": [1, 2],
    "status": "ativo",
    "notas": "Limpeza profissional"
  }'
```

### 4. Criar Feedbacks
```bash
# Feedback positivo para João (Acertou)
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
    "observacoes": "Excelente serviço, muito rápido",
    "seu_feedback": true
  }'

# Feedback com subestimação para João
curl -X POST http://localhost:8000/api/feedback \
  -H "Authorization: token" \
  -H "Content-Type: application/json" \
  -d '{
    "prestador_id": 1,
    "condominio_id": 2,
    "categoria_id": 1,
    "data_feedback": "2026-02-20",
    "qualidade": 4,
    "material_estimativa": "Subestimou 25-50%",
    "prazo_manteve": true,
    "custo_manteve": false,
    "observacoes": "Precisou de mais material, custo extra R$300",
    "seu_feedback": true
  }'

# Feedback positivo para Maria
curl -X POST http://localhost:8000/api/feedback \
  -H "Authorization: token" \
  -H "Content-Type: application/json" \
  -d '{
    "prestador_id": 2,
    "condominio_id": 1,
    "categoria_id": 2,
    "data_feedback": "2026-02-18",
    "qualidade": 4,
    "material_estimativa": "Acertou",
    "prazo_manteve": true,
    "custo_manteve": true,
    "observacoes": "Bom trabalho, preço justo",
    "seu_feedback": false
  }'

# Feedback negativo para Carlos (Atraso + Material)
curl -X POST http://localhost:8000/api/feedback \
  -H "Authorization: token" \
  -H "Content-Type: application/json" \
  -d '{
    "prestador_id": 3,
    "condominio_id": 1,
    "categoria_id": 3,
    "data_feedback": "2026-02-22",
    "qualidade": 3,
    "material_estimativa": "Subestimou >50%",
    "prazo_manteve": false,
    "custo_manteve": false,
    "observacoes": "Subestimou muito o material, atrasou 2 dias, custo +R$400",
    "seu_feedback": true
  }'
```

### 5. Verificar Scores
```bash
# Stats de João no Condomínio 1
curl "http://localhost:8000/api/feedback/stats/1?condominio_id=1"

# Stats de Maria no Condomínio 1
curl "http://localhost:8000/api/feedback/stats/2?condominio_id=1"

# Stats de Carlos no Condomínio 1
curl "http://localhost:8000/api/feedback/stats/3?condominio_id=1"
```

### 6. Ver Ranking
```bash
# Ranking de Condomínio 1
curl "http://localhost:8000/api/feedback/ranking/por-condominio/1"

# Ranking de Condomínio 1 só Encanaria
curl "http://localhost:8000/api/feedback/ranking/por-condominio/1?categoria_id=1"
```

### 7. Testar Chat
```bash
# Buscar encanador em Vargem
curl -X POST http://localhost:8000/api/chat/buscar \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "Preciso de um encanador em Vargem Grande Paulista"}'

# Buscar eletricista em Cotia
curl -X POST http://localhost:8000/api/chat/buscar \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "Eletricista em Cotia"}'
```

---

## Resultado Esperado

### João Silva (Encanaria)
- Feedback 1: Acertou, Prazo ✓, Custo ✓, Qualidade 5
- Feedback 2: Subestimou 25-50%, Prazo ✓, Custo ✗, Qualidade 4
- **Score:** Material (1.0/2) + Prazo (1.5/1.5) + Custo (0.75/1.5) + Qualidade (4.5/5) = **7.75**

### Maria Santos (Eletricista)
- Feedback 1: Acertou, Prazo ✓, Custo ✓, Qualidade 4
- **Score:** Material (2.0/2) + Prazo (1.5/1.5) + Custo (1.5/1.5) + Qualidade (4/5) = **9.0**

### Carlos Oliveira (Limpeza)
- Feedback 1: Subestimou >50%, Prazo ✗, Custo ✗, Qualidade 3
- **Score:** Material (0/2) + Prazo (0/1.5) + Custo (0/1.5) + Qualidade (3/5) = **3.0** (RISCO)

**Ranking esperado:**
1. Maria Santos (9.0)
2. João Silva (7.75)
3. Carlos Oliveira (3.0)

---

## Acessar Swagger UI

```
http://localhost:8000/docs
```

Ali você pode testar todos os endpoints visualmente com documentação interativa.

---

## Próximos Passos

1. ✅ Endpoints de Prestadores (CRUD)
2. ✅ Endpoints de Feedback (CRUD)
3. ⏳ Endpoints de Autenticação (Login/Register)
4. ⏳ Frontend React do Chat
5. ⏳ Frontend Admin Panel
