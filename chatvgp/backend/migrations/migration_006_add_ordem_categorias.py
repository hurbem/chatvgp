"""
Migration 006: Adicionar coluna 'ordem' na tabela categorias
- Controlar ordem de apresentação
"""

import psycopg2

def run_migration():
    """Adicionar coluna ordem na tabela categorias"""

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

        print("\n🔄 Migration 006: Adicionando coluna 'ordem' em categorias...")

        # Adicionar coluna ordem
        cursor.execute("""
            ALTER TABLE categorias
            ADD COLUMN IF NOT EXISTS ordem INTEGER DEFAULT 999;
        """)
        print("   ✅ Coluna 'ordem' adicionada")

        # Preencher com valores sequenciais (10, 20, 30...)
        cursor.execute("""
            UPDATE categorias SET ordem = (id * 10) WHERE ordem = 999;
        """)
        print("   ✅ Valores padrão preenchidos (10, 20, 30...)")

        # Criar índice
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_categorias_ordem ON categorias(ordem);
        """)
        print("   ✅ Índice criado")

        # Verificar estrutura
        cursor.execute("""
            SELECT column_name, data_type FROM information_schema.columns
            WHERE table_name='categorias'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()

        print("\n   📊 Estrutura da tabela categorias:")
        for col in columns:
            print(f"      - {col[0]}: {col[1]}")

        conn.commit()
        print("\n✅ Migration 006 completada com sucesso!\n")

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
