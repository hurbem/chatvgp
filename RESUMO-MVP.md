# ChatVGP MVP — Resumo do Projeto Criado

## O Que Foi Entregue

✅ **Estrutura completa** de pasta (backend + frontend)  
✅ **Models SQLAlchemy** (Usuário, Prestador, Categoria, Condomínio, Feedback)  
✅ **Schemas Pydantic** para validação de input/output  
✅ **Serviços de negócio**:
  - Ranking service: calcula score final com a lógica que mapeamos
  - Chat service: integra Claude API para entender perguntas em linguagem natural

✅ **Primeira rota funcional**: `/api/chat/buscar`  
✅ **Segurança**: hashing de senha (bcrypt), JWT tokens  
✅ **Configuração**: variáveis de ambiente, CORS, logs  

---

## Arquitetura Criada

```
chatvgp/
├── backend/
│   ├── app/
│   │   ├── models/        → SQLAlchemy models
│   │   ├── schemas/       → Pydantic validators
│   │   ├── routes/        → API endpoints
│   │   ├── services/      → Lógica de negócio
│   │   ├── utils/         → Segurança, JWT
│   │   ├── main.py        → FastAPI app
│   │   └── config.py      → Configurações
│   ├── requirements.txt    → Dependências Python
│   └── .env.example       → Variáveis de ambiente
```

---

## Stack Escolhido

| Camada | Tecnologia | Status |
|--------|-----------|--------|
| Backend | FastAPI + Python | ✅ Setup completo |
| Database | PostgreSQL | ✅ Models prontos |
| Auth | JWT + bcrypt | ✅ Implementado |
| IA | Claude API | ✅ Service criado |
| Frontend | React + TypeScript | ⏳ Próximo |

---

## Como Começar

### 1. Setup Backend (15 minutos)
```bash
cd chatvgp/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env com suas credenciais (PostgreSQL, Claude API)
uvicorn app.main:app --reload
```

### 2. Testar API
Acessar http://localhost:8000/docs

Exemplo de request:
```bash
curl -X POST "http://localhost:8000/api/chat/buscar" \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "Preciso de um encanador em Vargem Grande Paulista"}'
```

---

## O Que a IA (Claude) Faz Nesta Arquitetura

1. **Entender pergunta**: Quando cliente digita "Preciso de encanador", Claude interpreta
2. **Extrair categoria**: Mapeia "encanador" → categoria_id
3. **Extrair condomínio**: Se mencionado ("em Vargem"), extrai condominio_id
4. **Retornar top 5**: Com base no score de ranking

**Custo**: ~R$0.003 por pergunta (muito barato)

---

## Score Final (Implementado)

Cada prestador recebe uma nota baseada em:

```
Score Final = (Material Acertou % × 2) + (Prazo Cumprido % × 1.5) + (Custo Mantido % × 1.5) + Qualidade Média

Máximo: ~10 pontos
Interpretação:
  > 8 = Excelente
  6-8 = Bom
  4-6 = Regular
  < 4 = Risco
```

---

## Próximos Passos

### Imediato (1-2 dias)
- [ ] Criar rotas de Prestadores (CRUD) → /api/prestadores
- [ ] Criar rotas de Feedback (POST) → /api/feedback
- [ ] Criar rotas de Admin → /api/admin
- [ ] Autenticação (login/senha) → /api/auth/login

### Curto Prazo (3-5 dias)
- [ ] Frontend do chat (React)
- [ ] Admin panel (CRUD de prestadores)
- [ ] Testes do backend

### Deploy
- [ ] PostgreSQL em Render
- [ ] Backend em Render
- [ ] Frontend em Vercel

---

## Segurança: Checklist

- [x] Senha com hash (bcrypt)
- [x] JWT para autenticação
- [x] SQL injection prevention (SQLAlchemy parameterizado)
- [x] CORS configurado
- [x] Variáveis de ambiente (.env)
- [ ] Rate limiting (próximo)
- [ ] Logs de auditoria (próximo)
- [ ] HTTPS forçado (Render/Vercel automático)

---

## Dúvidas Frequentes

**P: Preciso realmente de PostgreSQL agora?**  
R: Sim, está mapeado. Use Render gratuito ou Docker local.

**P: Onde coloco minha Claude API key?**  
R: Em `.env` → `CLAUDE_API_KEY=sk-xxx`

**P: Posso mudar a mensagem do WhatsApp?**  
R: Sim, em `app/services/chat_service.py` na função `gerar_link_whatsapp()`

**P: O chat entenderá "bombeiro" também?**  
R: Sim, Claude mapeia sinônimos. Basta ter "Encanaria" como categoria.

---

## Arquivos Principais

- `app/main.py` — Entry point (inicia o servidor)
- `app/services/chat_service.py` — Lógica de IA + busca
- `app/services/ranking_service.py` — Cálculo de score
- `app/models/` — Database models
- `app/schemas/` — Validação de input/output
- `SETUP.md` — Instruções detalhadas
