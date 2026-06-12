"""
Migration 004: Update prestadores table
- Add UNIQUE constraint to whatsapp
- Remove categoria_id column
- Remove indicacoes_moradores column
"""

import psycopg2

def run_migration():
    """Update prestadores table structure"""

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

        print("\n🔄 Migration 004: Atualizando tabela prestadores...")

        # 1. Add UNIQUE constraint to whatsapp
        try:
            cursor.execute("""
                ALTER TABLE prestadores
                ADD CONSTRAINT prestadores_whatsapp_unique UNIQUE (whatsapp)
            """)
            print("   ✅ UNIQUE constraint adicionado a whatsapp")
        except Exception as e:
            print(f"   ⚠️  whatsapp unique: {e}")

        # 2. Remove categoria_id FK constraint
        try:
            cursor.execute("""
                ALTER TABLE prestadores
                DROP CONSTRAINT IF EXISTS prestadores_categoria_id_fkey
            """)
            print("   ✅ Foreign key categoria_id removida")
        except Exception as e:
            print(f"   ⚠️  FK categoria: {e}")

        # 3. Remove categoria_id column
        try:
            cursor.execute("""
                ALTER TABLE prestadores
                DROP COLUMN IF EXISTS categoria_id
            """)
            print("   ✅ Coluna categoria_id removida")
        except Exception as e:
            print(f"   ⚠️  categoria_id: {e}")

        # 4. Remove indicacoes_moradores column
        try:
            cursor.execute("""
                ALTER TABLE prestadores
                DROP COLUMN IF EXISTS indicacoes_moradores
            """)
            print("   ✅ Coluna indicacoes_moradores removida")
        except Exception as e:
            print(f"   ⚠️  indicacoes_moradores: {e}")

        # 5. Verificar estrutura final
        cursor.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name='prestadores'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()

        print("\n   📊 Colunas finais da tabela prestadores:")
        for col in columns:
            print(f"      - {col[0]}")

        conn.commit()
        print("\n✅ Migration 004 completada com sucesso!\n")

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
