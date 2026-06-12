#!/bin/bash
# Roda uma migration .sql dentro do container Postgres do Docker.
#
# Uso:
#   ./run_migration_docker.sh migration_006_add_ordem_categorias.sql
#
# Variáveis opcionais (sobrescrevem os defaults do setup-local.sh):
#   CONTAINER (default: chatvgp-db)
#   PGUSER    (default: postgres)
#   PGDATABASE (default: chatvgp)

set -e

CONTAINER="${CONTAINER:-chatvgp-db}"
PGUSER="${PGUSER:-postgres}"
PGDATABASE="${PGDATABASE:-chatvgp}"

if [ -z "$1" ]; then
  echo "Uso: $0 <arquivo_migration.sql>"
  exit 1
fi

SQL_FILE="$1"
DIR="$(cd "$(dirname "$0")" && pwd)"
SQL_PATH="$DIR/$SQL_FILE"

if [ ! -f "$SQL_PATH" ]; then
  echo "❌ Arquivo não encontrado: $SQL_PATH"
  exit 1
fi

if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
  echo "❌ Container '$CONTAINER' não está rodando."
  echo "   Verifique com: docker ps"
  exit 1
fi

echo "🔄 Aplicando $SQL_FILE no container '$CONTAINER' (db: $PGDATABASE)..."
docker exec -i "$CONTAINER" psql -U "$PGUSER" -d "$PGDATABASE" < "$SQL_PATH"
echo "✅ Migration aplicada com sucesso!"
