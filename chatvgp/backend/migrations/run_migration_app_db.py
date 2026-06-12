"""
Aplica um arquivo .sql usando o MESMO DATABASE_URL configurado no .env do backend
(app.config.settings). Útil para garantir que a migration vai para o banco que
o backend realmente usa — independente de ser o Postgres do Docker ou um
Postgres nativo rodando na mesma porta.

Uso:
    python migrations/run_migration_app_db.py migrations/migration_006_add_ordem_categorias.sql
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine, text
from app.config import settings


def main():
    if len(sys.argv) < 2:
        print("Uso: python run_migration_app_db.py <arquivo.sql>")
        sys.exit(1)

    sql_path = sys.argv[1]
    if not os.path.isfile(sql_path):
        print(f"❌ Arquivo não encontrado: {sql_path}")
        sys.exit(1)

    with open(sql_path, "r") as f:
        sql = f.read()

    print(f"🔄 Conectando em: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)

    with engine.begin() as conn:
        for statement in [s.strip() for s in sql.split(";") if s.strip()]:
            print(f"   -> {statement.splitlines()[0]}...")
            conn.execute(text(statement))

    print("✅ Migration aplicada com sucesso no banco do backend!")


if __name__ == "__main__":
    main()
