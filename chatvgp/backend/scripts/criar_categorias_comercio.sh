#!/bin/bash
API_URL="${API_URL:-https://chatvgp-api.onrender.com}"
SECRET_KEY="almDe44dPMXo2V1axX20DfkQpckyaN4Z2J8OzjiXWbU"

echo "🔐 Fazendo login..."
TOKEN=$(curl -s -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Mozilla/5.0" \
  -d "{\"senha\": \"$SECRET_KEY\"}" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

if [ -z "$TOKEN" ]; then
  echo "❌ Falha no login."
  exit 1
fi
echo "✅ Token obtido"
echo ""

criar_categoria() {
  local NOME="$1"
  local DESCRICAO="$2"
  echo -n "📂 Criando '$NOME'... "
  RESP=$(curl -s -X POST "$API_URL/api/categorias" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -H "User-Agent: Mozilla/5.0" \
    -d "{\"nome\": \"$NOME\", \"descricao\": \"$DESCRICAO\"}")
  echo "$RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if 'id' in d else d.get('detail','ERRO'))" 2>/dev/null || echo "ERRO: $RESP"
  sleep 2
}

criar_categoria "Hortifruti"   "Frutas, verduras, legumes e produtos frescos"
criar_categoria "Farmácia"     "Medicamentos, produtos de saúde e higiene"
criar_categoria "Escola"       "Escolas, cursos, creches e educação infantil"
criar_categoria "Veterinária"  "Consultas, vacinas e cuidados com animais de estimação"

echo ""
echo "✅ Concluído!"
