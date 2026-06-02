# ChatVGP API — Endpoints Implementados

## Status: ✅ Prestadores, Categorias, Condomínios, Chat, Feedback

---

## Autenticação

Endpoints protegidos (admin) requerem header:
```
Authorization: any-token-here
```

Para MVP, qualquer valor não-vazio funciona. Em produção, usar JWT proper.

---

## Categorias

### GET `/api/categorias`
Listar todas as categorias (público).

**Exemplo:**
```bash
curl http://localhost:8000/api/categorias
```

**Response:**
```json
[
  {
    "id": 1,
    "nome": "Encanaria",
    "descricao": "Serviços hidráulicos"
  },
  {
    "id": 2,
    "nome": "Eletricista",
    "descricao": "Instalação elétrica"
  }
]
```

### POST `/api/categorias`
Criar nova categoria (admin only).

**Headers:**
```
Authorization: token
```

**Body:**
```json
{
  "nome": "Pintura",
  "descricao": "Pintura residencial"
}
```

**Comando:**
```bash
curl -X POST http://localhost:8000/api/categorias \
  -H "Authorization: token" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Pintura", "descricao": "Pintura residencial"}'
```

### PUT `/api/categorias/{id}`
Atualizar categoria (admin only).

### DELETE `/api/categorias/{id}`
Deletar categoria (admin only).

---

## Condomínios

### GET `/api/condominios`
Listar condomínios (público).

**Parâmetros:**
- `cidade` (opcional): filtrar por cidade

**Exemplo:**
```bash
curl http://localhost:8000/api/condominios?cidade=Vargem%20Grande%20Paulista
```

### POST `/api/condominios`
Criar novo condomínio (admin only).

**Body:**
```json
{
  "nome": "Condomínio A",
  "cidade": "Vargem Grande Paulista"
}
```

**Comando:**
```bash
curl -X POST http://localhost:8000/api/condominios \
  -H "Authorization: token" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Condomínio A", "cidade": "Vargem Grande Paulista"}'
```

### PUT `/api/condominios/{id}`
Atualizar condomínio (admin only).

### DELETE `/api/condominios/{id}`
Deletar condomínio (admin only).

---

## Prestadores

### GET `/api/prestadores`
Listar prestadores com scores (público).

**Parâmetros:**
- `categoria_id` (opcional): filtrar por categoria
- `condominio_id` (opcional): filtrar por condomínio
- `status_filter` (opcional): "ativo" ou "inativo"

**Exemplo:**
```bash
curl "http://localhost:8000/api/prestadores?categoria_id=1&status_filter=ativo"
```

**Response:**
```json
[
  {
    "id": 1,
    "nome": "João Silva",
    "whatsapp": "11999887766",
    "categoria_id": 1,
    "condominio_ids": [1, 2],
    "status": "ativo",
    "notas": "Excelente encanador",
    "criado_em": "2026-02-15T10:30:00",
    "categoria": {
      "id": 1,
      "nome": "Encanaria",
      "descricao": null
    },
    "score_final": 8.5,
    "feedback_count": 5,
    "qualidade_media": 4.8,
    "material_acertou_pct": 0.8,
    "prazo_cumprido_pct": 1.0,
    "custo_mantido_pct": 0.8
  }
]
```

### GET `/api/prestadores/{id}`
Obter detalhes de um prestador com score (público).

**Exemplo:**
```bash
curl http://localhost:8000/api/prestadores/1
```

### POST `/api/prestadores`
Criar novo prestador (admin only).

**Headers:**
```
Authorization: token
```

**Body:**
```json
{
  "nome": "Maria Santos",
  "whatsapp": "11988776655",
  "categoria_id": 2,
  "condominio_ids": [1],
  "status": "ativo",
  "notas": "Eletricista com 10 anos de experiência"
}
```

**Comando:**
```bash
curl -X POST http://localhost:8000/api/prestadores \
  -H "Authorization: token" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria Santos",
    "whatsapp": "11988776655",
    "categoria_id": 2,
    "condominio_ids": [1],
    "status": "ativo",
    "notas": "Eletricista experiente"
  }'
```

### PUT `/api/prestadores/{id}`
Atualizar prestador (admin only).

**Body:** (atualizar apenas campos desejados)
```json
{
  "status": "inativo",
  "notas": "Não atende mais"
}
```

**Comando:**
```bash
curl -X PUT http://localhost:8000/api/prestadores/1 \
  -H "Authorization: token" \
  -H "Content-Type: application/json" \
  -d '{"status": "inativo"}'
```

### DELETE `/api/prestadores/{id}`
Deletar prestador (admin only).

**Comando:**
```bash
curl -X DELETE http://localhost:8000/api/prestadores/1 \
  -H "Authorization: token"
```

---

## Chat (Busca de Prestadores)

### POST `/api/chat/buscar`
Buscar prestadores por pergunta em linguagem natural (público).

**Body:**
```json
{
  "pergunta": "Preciso de um encanador em Vargem Grande Paulista",
  "condominio_id": null
}
```

**Comando:**
```bash
curl -X POST http://localhost:8000/api/chat/buscar \
  -H "Content-Type: application/json" \
  -d '{
    "pergunta": "Preciso de um encanador em Vargem Grande Paulista"
  }'
```

**Response:**
```json
{
  "pergunta": "Preciso de um encanador em Vargem Grande Paulista",
  "categoria": "Encanaria",
  "condominio": "Vargem Grande Paulista",
  "prestadores": [
    {
      "id": 1,
      "nome": "João Silva",
      "whatsapp": "11999887766",
      "link_whatsapp": "https://wa.me/5511999887766?text=...",
      "score_final": 8.5,
      "feedback_count": 5,
      "qualidade_media": 4.8,
      "material_acertou_pct": 0.8,
      "prazo_cumprido_pct": 1.0,
      "custo_mantido_pct": 0.8
    }
  ],
  "total_resultados": 1
}
```

---

## Feedback

### GET `/api/feedback`
Listar feedbacks com filtros (público).

**Parâmetros:**
- `prestador_id` (opcional): filtrar por prestador
- `condominio_id` (opcional): filtrar por condomínio
- `categoria_id` (opcional): filtrar por categoria
- `seu_feedback` (opcional): true/false
- `skip` (opcional): paginação (padrão: 0)
- `limit` (opcional): quantidade (padrão: 100)

**Exemplo:**
```bash
curl "http://localhost:8000/api/feedback?prestador_id=1&condominio_id=1"
```

**Response:**
```json
[
  {
    "id": 1,
    "prestador_id": 1,
    "condominio_id": 1,
    "categoria_id": 1,
    "data_feedback": "2026-02-15",
    "qualidade": 5,
    "material_estimativa": "Acertou",
    "prazo_manteve": true,
    "custo_manteve": true,
    "observacoes": "Excelente serviço",
    "seu_feedback": true,
    "criado_em": "2026-02-15T10:30:00"
  }
]
```

### GET `/api/feedback/prestador/{prestador_id}`
Listar feedbacks de um prestador específico (público).

**Exemplo:**
```bash
curl http://localhost:8000/api/feedback/prestador/1
```

### GET `/api/feedback/{id}`
Obter detalhes de um feedback (público).

**Exemplo:**
```bash
curl http://localhost:8000/api/feedback/1
```

### GET `/api/feedback/stats/{prestador_id}`
Obter estatísticas agregadas de um prestador (público).

**Parâmetros:**
- `condominio_id` (opcional): se não especificado, usa o primeiro condomínio do prestador

**Exemplo:**
```bash
curl "http://localhost:8000/api/feedback/stats/1?condominio_id=1"
```

**Response:**
```json
{
  "qualidade_media": 4.8,
  "material_acertou_pct": 0.8,
  "prazo_cumprido_pct": 1.0,
  "custo_mantido_pct": 0.8,
  "total_feedbacks": 5,
  "score_material": 1.6,
  "score_prazo": 1.5,
  "score_custo": 1.2,
  "score_qualidade": 4.8,
  "score_final": 9.1
}
```

### POST `/api/feedback`
Criar novo feedback (admin only).

**Headers:**
```
Authorization: token
```

**Body:**
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
  "observacoes": "Excelente serviço, rápido e eficiente",
  "seu_feedback": true
}
```

**Material_estimativa válidos:**
- `"Acertou"`
- `"Subestimou 10-25%"`
- `"Subestimou 25-50%"`
- `"Subestimou >50%"`

**Comando:**
```bash
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
    "observacoes": "Ótimo trabalho",
    "seu_feedback": true
  }'
```

### PUT `/api/feedback/{id}`
Atualizar feedback (admin only).

**Body:** (atualizar apenas campos desejados)
```json
{
  "qualidade": 4,
  "observacoes": "Bom, mas atrasou 1 dia"
}
```

**Comando:**
```bash
curl -X PUT http://localhost:8000/api/feedback/1 \
  -H "Authorization: token" \
  -H "Content-Type: application/json" \
  -d '{"qualidade": 4}'
```

### DELETE `/api/feedback/{id}`
Deletar feedback (admin only).

**Comando:**
```bash
curl -X DELETE http://localhost:8000/api/feedback/1 \
  -H "Authorization: token"
```

### GET `/api/feedback/ranking/por-condominio/{condominio_id}`
Obter ranking de prestadores em um condomínio (público).

**Parâmetros:**
- `categoria_id` (opcional): filtrar por categoria
- `limit` (opcional): quantidade (padrão: 10)

**Exemplo:**
```bash
curl "http://localhost:8000/api/feedback/ranking/por-condominio/1?categoria_id=1&limit=5"
```

**Response:**
```json
[
  {
    "id": 1,
    "nome": "João Silva",
    "whatsapp": "11999887766",
    "categoria": "Encanaria",
    "score_final": 9.1,
    "posicao": 1,
    "qualidade_media": 4.8,
    "material_acertou_pct": 0.8,
    "prazo_cumprido_pct": 1.0,
    "custo_mantido_pct": 0.8,
    "feedback_count": 5
  },
  {
    "id": 2,
    "nome": "Maria Santos",
    "whatsapp": "11988776655",
    "categoria": "Eletricista",
    "score_final": 7.5,
    "posicao": 2,
    "qualidade_media": 4.3,
    "material_acertou_pct": 0.6,
    "prazo_cumprido_pct": 1.0,
    "custo_mantido_pct": 0.6,
    "feedback_count": 3
  }
]
```

---

## Endpoints Planejados (Próximo)

- [ ] `POST /api/auth/login` — Login admin (com JWT)
- [ ] `POST /api/auth/register` — Criar conta admin
- [ ] `GET /api/admin/dashboard` — Dashboard admin
- [ ] `GET /api/admin/relatorios` — Relatórios e análises

---

## Como Testar Localmente

1. Inicie o servidor:
```bash
cd chatvgp/backend
uvicorn app.main:app --reload
```

2. Acesse Swagger UI:
```
http://localhost:8000/docs
```

3. Ou use curl (exemplos acima)

4. Para endpoints protegidos, adicione header:
```
Authorization: any-token
```

---

## Notas de Segurança

**MVP:** Header `Authorization` é aceito sem validação (qualquer valor não-vazio).

**Produção:** Implementar JWT validation:
- Gerar token no login
- Validar token em endpoints protegidos
- Adicionar expiração de token

Ver `app/utils/security.py` para funções já criadas.
