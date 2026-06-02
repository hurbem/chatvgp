#!/bin/bash

set -e  # Exit on error

echo "🚀 ChatVGP - Setup Local"
echo "======================="
echo ""

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. PostgreSQL
echo -e "${BLUE}1. Iniciando PostgreSQL via Docker...${NC}"
docker run --name chatvgp-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=chatvgp \
  -p 5432:5432 \
  -d postgres:15 2>/dev/null || echo "Container já existe"

sleep 2
echo -e "${GREEN}✓ PostgreSQL rodando em localhost:5432${NC}"
echo ""

# 2. Backend - Create .env
echo -e "${BLUE}2. Configurando Backend (.env)...${NC}"
cd chatvgp/backend

cat > .env << 'EOF'
DATABASE_URL=postgresql://postgres:password@localhost:5432/chatvgp
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CLAUDE_API_KEY=sk-placeholder-for-testing
ENVIRONMENT=development
DEBUG=True
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://localhost:8000"]
EOF

echo -e "${GREEN}✓ .env criado${NC}"
echo ""

# 3. Install Python deps
echo -e "${BLUE}3. Instalando dependências Python...${NC}"
python3 -m pip install -q -r requirements.txt 2>/dev/null || true
echo -e "${GREEN}✓ Dependências instaladas${NC}"
echo ""

# 4. Backend em background
echo -e "${BLUE}4. Iniciando Backend em porta 8000...${NC}"
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
sleep 3

if ps -p $BACKEND_PID > /dev/null; then
  echo -e "${GREEN}✓ Backend rodando (PID: $BACKEND_PID)${NC}"
else
  echo "❌ Backend falhou ao iniciar"
  exit 1
fi
echo ""

# 5. Frontend
echo -e "${BLUE}5. Frontend já está rodando em http://localhost:5173${NC}"
echo ""

echo -e "${GREEN}✅ Setup Completo!${NC}"
echo ""
echo "URLs disponíveis:"
echo "  • Frontend:  http://localhost:5173"
echo "  • Backend:   http://localhost:8000"
echo "  • Swagger:   http://localhost:8000/docs"
echo ""
echo "Próximos passos:"
echo "  1. Abra http://localhost:5173 no navegador"
echo "  2. Clique no botão 🔐 Admin"
echo "  3. Use token: 'admin-token'"
echo "  4. Cadastre prestadores de teste"
echo "  5. Teste a busca"
echo ""
echo "Para parar tudo: Ctrl+C (aqui)"
echo ""

wait
