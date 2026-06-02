# ChatVGP Frontend

React + TypeScript + Tailwind CSS

## Setup

### 1. Instalar dependências
```bash
cd chatvgp/frontend
npm install
```

### 2. Configurar variáveis de ambiente
```bash
cp .env.example .env
# Editar .env se necessário (por padrão usa http://localhost:8000/api)
```

### 3. Rodar servidor de desenvolvimento
```bash
npm start
```

Acessa: `http://localhost:3000`

## Estrutura

```
src/
├── components/        # Componentes reutilizáveis
│   ├── ChatInput.tsx
│   ├── ChatResult.tsx
│   └── PrestadorCard.tsx
├── pages/            # Páginas principais
│   ├── ChatPage.tsx   # Interface pública do chat
│   └── AdminPage.tsx  # Painel admin
├── services/         # Serviços (API client)
│   └── api.ts
├── types/            # TypeScript types
│   └── index.ts
├── App.tsx           # Componente raiz + roteamento
├── index.tsx         # Entry point
└── index.css         # Estilos globais
```

## Páginas Implementadas

### ChatPage (Pública)
- Interface de busca com input
- Exibição de resultados
- Cartões de prestadores com scores
- Histórico de buscas

### AdminPage (Protegida por Token)
- Abas: Prestadores, Feedback, Ranking
- Form para cadastrar prestadores
- Tabela de prestadores
- Login simples com token

## Como Testar

1. **Rodar backend:**
   ```bash
   cd chatvgp/backend
   uvicorn app.main:app --reload
   ```

2. **Rodar frontend:**
   ```bash
   cd chatvgp/frontend
   npm start
   ```

3. **Acessar:**
   - Chat público: `http://localhost:3000`
   - Admin: Clique em "🔐 Admin", use token "admin-token"

## Próximos Passos

- [ ] Form de feedback na aba Feedback
- [ ] View de ranking na aba Ranking
- [ ] Autenticação com JWT (atual usa token simples)
- [ ] Responsividade mobile
- [ ] Testes unitários
- [ ] Temas (dark mode)

## Build para Produção

```bash
npm run build
```

Gera pasta `build/` pronta para deploy (Vercel, Netlify, etc).
