#!/bin/bash

# Script para inserir 5 prestadores via API
API_URL="https://chatvgp-api.onrender.com/api/prestadores"

echo "🚀 Inserindo 5 prestadores na categoria Encanador..."

# Prestador 1
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Carlos Silva - Encanador",
    "whatsapp": "11987654321",
    "categoria_id": 1,
    "condominio_ids": [2],
    "status": "ativo",
    "notas": "Especialista em hidráulica residencial"
  }' && echo -e "\n✅ Carlos inserido"

# Prestador 2
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Roberto Santos",
    "whatsapp": "11987654322",
    "categoria_id": 1,
    "condominio_ids": [2],
    "status": "ativo",
    "notas": "Atua há 15 anos na região"
  }' && echo -e "\n✅ Roberto inserido"

# Prestador 3
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Felipe Oliveira",
    "whatsapp": "11987654323",
    "categoria_id": 1,
    "condominio_ids": [2],
    "status": "ativo",
    "notas": "Reparos urgentes 24h"
  }' && echo -e "\n✅ Felipe inserido"

# Prestador 4
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Marcelo Costa",
    "whatsapp": "11987654324",
    "categoria_id": 1,
    "condominio_ids": [2],
    "status": "ativo",
    "notas": "Orçamentos sem custo"
  }' && echo -e "\n✅ Marcelo inserido"

# Prestador 5
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "André Pereira",
    "whatsapp": "11987654325",
    "categoria_id": 1,
    "condominio_ids": [2],
    "status": "ativo",
    "notas": "Trabalho com garantia"
  }' && echo -e "\n✅ André inserido"

echo -e "\n🎉 Inserção concluída!"
