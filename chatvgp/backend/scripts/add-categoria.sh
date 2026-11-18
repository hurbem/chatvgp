#!/bin/bash
# ============================================================
# Cria uma ou mais categorias no ChatVGP via API.
# Os aliases de busca são gerados automaticamente pelo Claude.
#
# Uso:
#   ADMIN_PASSWORD='sua-senha' ./add-categoria.sh "Nome" "Descrição" ["Nome 2" "Descrição 2" ...]
#
# Exemplo:
#   ADMIN_PASSWORD='...' ./add-categoria.sh "Banho e Tosa" "Banho, tosa e higiene para pets."
#
# Para usar a API local:  API_URL=http://localhost:8000 ADMIN_PASSWORD=... ./add-categoria.sh ...
# ============================================================
set -euo pipefail

API_URL="${API_URL:-https://chatvgp-api.onrender.com}"
SENHA="${ADMIN_PASSWORD:?Defina ADMIN_PASSWORD. Ex: ADMIN_PASSWORD='sua-senha' $0 \"Nome\" \"Descrição\"}"

if [ $# -lt 2 ] || [ $(( $# % 2 )) -ne 0 ]; then
  echo "Uso: ADMIN_PASSWORD='...' $0 \"Nome\" \"Descrição\" [\"Nome 2\" \"Descrição 2\" ...]"
  exit 1
fi

# Monta JSON com segurança (aspas e acentos) usando Python
json() { python3 -c 'import json,sys; print(json.dumps(dict(zip(sys.argv[1::2], sys.argv[2::2]))))' "$@"; }

echo "🔐 Fazendo login em $API_URL..."
TOKEN=$(curl -s -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Mozilla/5.0" \
  -d "$(json senha "$SENHA")" \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))")

if [ -z "$TOKEN" ]; then
  echo "❌ Falha no login. Verifique ADMIN_PASSWORD e API_URL."
  exit 1
fi

while [ $# -gt 0 ]; do
  NOME="$1"; DESCRICAO="$2"; shift 2
  echo -n "📂 Criando '$NOME'... "
  curl -s -X POST "$API_URL/api/categorias" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -H "User-Agent: Mozilla/5.0" \
    -d "$(json nome "$NOME" descricao "$DESCRICAO")" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print('✅ aliases: ' + (d.get('aliases') or '(nenhum)') if 'id' in d else '❌ ' + str(d.get('detail', d)))"
  sleep 2  # evita o rate limit
done

echo "✅ Concluído!"
