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

criar_categoria "Doces e Bolos" "Confeitaria, bolos personalizados, doces e encomendas"
criar_categoria "Piscinas"      "Limpeza, manutenção e instalação de piscinas"

echo ""
echo "✅ Concluído!"
