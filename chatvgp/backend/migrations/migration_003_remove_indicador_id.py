"""
Migration 003: Remove indicador_id column from prestadores table
"""

import psycopg2
from psycopg2 import sql

def run_migration():
    """Remove indicador_id column and its foreign key constraint"""

    conn = None
    cursor = None

    try:
        # Conexão
        conn = psycopg2.connect(
            host="localhost",
            database="chatvgp",
            user="postgres",
            password="password",
            port=5432
        )
        cursor = conn.cursor()

        print("\n🔄 Migration 003: Removendo coluna indicador_id...")

        # 1. Remover constraint de FK
        try:
            cursor.execute("""
                ALTER TABLE prestadores
                DROP CONSTRAINT IF EXISTS prestadores_indicador_id_fkey
            """)
            print("   ✅ Foreign key removida")
        except Exception as e:
            print(f"   ⚠️  FK não encontrada: {e}")

        # 2. Remover coluna
        cursor.execute("""
            ALTER TABLE prestadores
            DROP COLUMN IF EXISTS indicador_id
        """)
        print("   ✅ Coluna indicador_id removida")

        # 3. Verificar estrutura
        cursor.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name='prestadores'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()

        print("\n   📊 Colunas da tabela prestadores:")
        for col in columns:
            print(f"      - {col[0]}")

        conn.commit()
        print("\n✅ Migration 003 completada com sucesso!\n")

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
