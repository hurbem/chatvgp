#!/bin/bash
# ============================================================
# Script: criar_categorias.sh
# Cria categorias no ChatVGP via API (aliases gerados pelo Claude)
# ============================================================
# Uso:
#   chmod +x criar_categorias.sh
#   API_URL=https://chatvgp-api.onrender.com SECRET_KEY=sua_chave ./criar_categorias.sh
# ============================================================

API_URL="${API_URL:-https://chatvgp-api.onrender.com}"
SECRET_KEY="almDe44dPMXo2V1axX20DfkQpckyaN4Z2J8OzjiXWbU"

if [ -z "$SECRET_KEY" ]; then
  echo "❌ Defina a variável SECRET_KEY antes de rodar"
  echo "   Exemplo: SECRET_KEY=sua_chave ./criar_categorias.sh"
  exit 1
fi

# ----------------------------------------------------------
# 1. Login — obtém token JWT
# ----------------------------------------------------------
echo "🔐 Fazendo login..."
TOKEN=$(curl -s -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Mozilla/5.0" \
  -d "{\"senha\": \"$SECRET_KEY\"}" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

if [ -z "$TOKEN" ]; then
  echo "❌ Falha no login. Verifique a SECRET_KEY e a URL da API."
  exit 1
fi
echo "✅ Token obtido"
echo ""

# ----------------------------------------------------------
# 2. Função auxiliar para criar categoria
# ----------------------------------------------------------
criar_categoria() {
  local NOME="$1"
  local DESCRICAO="$2"

  echo -n "📂 Criando '$NOME'... "
  RESP=$(curl -s -X POST "$API_URL/api/categorias" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -H "User-Agent: Mozilla/5.0" \
    -d "{\"nome\": \"$NOME\", \"descricao\": \"$DESCRICAO\"}")

  # Verifica se criou ou já existe
  if echo "$RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if 'id' in d else d.get('detail','ERRO'))" 2>/dev/null; then
    :
  else
    echo "ERRO: $RESP"
  fi

  # Pausa entre requests para não sobrecarregar a Claude API
  sleep 2
}

# ----------------------------------------------------------
# 3. Categorias ordenadas por popularidade
# ----------------------------------------------------------

criar_categoria "Eletricista"         "Instalações e reparos elétricos residenciais e comerciais"
criar_categoria "Encanador"           "Serviços de hidráulica, encanamento e reparos de vazamento"
criar_categoria "Diarista"            "Limpeza e organização residencial"
criar_categoria "Pedreiro"            "Reformas, alvenaria e serviços de construção civil"
criar_categoria "Pintor"              "Pintura interna e externa, textura e grafiato"
criar_categoria "Mecânico"            "Manutenção e reparo de veículos"
criar_categoria "Chaveiro"            "Chaves, fechaduras, abertura de portas e cofres"
criar_categoria "Jardineiro"          "Manutenção de jardins, poda e paisagismo"
criar_categoria "Técnico de Informática" "Manutenção, formatação e suporte de computadores e redes"
criar_categoria "Ar-Condicionado"     "Instalação, manutenção e limpeza de ar-condicionado"
criar_categoria "Marceneiro"          "Móveis planejados, reparos e trabalhos em madeira"
criar_categoria "Serralheiro"         "Grades, portões, escadas e trabalhos em metal"
criar_categoria "Vidraceiro"          "Instalação e reparo de vidros, janelas e espelhos"
criar_categoria "Gesseiro"            "Forro de gesso, drywall e acabamentos"
criar_categoria "Dedetizador"         "Controle de pragas, cupins, baratas e roedores"
criar_categoria "Cuidador de Idosos"  "Acompanhamento e cuidados com pessoas idosas"
criar_categoria "Babá"                "Cuidados com crianças"
criar_categoria "Cabeleireiro"        "Corte, coloração e tratamentos capilares"
criar_categoria "Manicure"            "Unhas, pedicure e esmaltação"
criar_categoria "Fotógrafo"           "Fotografia de eventos, família e corporativa"
criar_categoria "Professor Particular" "Aulas e reforço escolar particulares"
criar_categoria "Personal Trainer"    "Treinos personalizados e condicionamento físico"
criar_categoria "Nutricionista"       "Orientação nutricional e planos alimentares"
criar_categoria "Marmoraria"          "Bancadas, pias e trabalhos em pedra e granito"
criar_categoria "Designer Gráfico"    "Criação de logotipos, artes e materiais gráficos"

echo ""
echo "✅ Concluído!"
