"""
Migration 005: Implementar relação many-to-many prestador x categoria
- Criar tabela prestador_categorias
"""

import psycopg2

def run_migration():
    """Criar tabela prestador_categorias para relação many-to-many"""

    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(
            host="localhost",
            database="chatvgp",
            user="postgres",
            password="password",
            port=5432
        )
        cursor = conn.cursor()

        print("\n🔄 Migration 005: Criando tabela prestador_categorias...")

        # Criar tabela prestador_categorias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prestador_categorias (
                id SERIAL PRIMARY KEY,
                prestador_id INTEGER NOT NULL REFERENCES prestadores(id) ON DELETE CASCADE,
                categoria_id INTEGER NOT NULL REFERENCES categorias(id) ON DELETE CASCADE,
                UNIQUE(prestador_id, categoria_id)
            );

            CREATE INDEX IF NOT EXISTS idx_prestador_categorias_prestador_id
            ON prestador_categorias(prestador_id);

            CREATE INDEX IF NOT EXISTS idx_prestador_categorias_categoria_id
            ON prestador_categorias(categoria_id);
        """)
        print("   ✅ Tabela prestador_categorias criada com índices")

        # Verificar estrutura
        cursor.execute("""
            SELECT column_name, data_type FROM information_schema.columns
            WHERE table_name='prestador_categorias'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()

        print("\n   📊 Estrutura da tabela prestador_categorias:")
        for col in columns:
            print(f"      - {col[0]}: {col[1]}")

        conn.commit()
        print("\n✅ Migration 005 completada com sucesso!\n")

    except Exception as e:
        print(f"\n❌ Erro na migration: {e}\n")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    run_migration()
