#!/usr/bin/env python3
"""
Migração: Refatoração do schema de Prestador

Mudanças:
  ❌ REMOVE: condominio_ids (array) - agora em Feedback
  ✅ ADD: instagram (VARCHAR 500) - link do perfil
  ✅ ADD: site (VARCHAR 500) - endereço web

Executar: python migrations/001_refactor_prestador.py
"""

import sys
import os

# Adicionar backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import text
from app.database import engine

def run_migration():
    """Executa a migração"""

    print("\n" + "="*60)
    print("🔄 MIGRAÇÃO: Refatoração de Prestador")
    print("="*60)

    try:
        with engine.connect() as conn:
            # ===== REMOVER COLUNA ANTIGA =====
            print("\n📋 Etapa 1: Removendo coluna antiga...")
            print("  ❌ Removendo: condominio_ids")

            conn.execute(text("""
                ALTER TABLE prestadores
                DROP COLUMN IF EXISTS condominio_ids CASCADE;
            """))
            print("     ✅ Coluna removida com sucesso")

            # ===== ADICIONAR NOVAS COLUNAS =====
            print("\n📋 Etapa 2: Adicionando novas colunas...")
            print("  ✅ Adicionando: instagram (VARCHAR 500)")
            print("  ✅ Adicionando: site (VARCHAR 500)")

            conn.execute(text("""
                ALTER TABLE prestadores
                ADD COLUMN IF NOT EXISTS instagram VARCHAR(500),
                ADD COLUMN IF NOT EXISTS site VARCHAR(500);
            """))
            print("     ✅ Colunas adicionadas com sucesso")

            # ===== COMMIT =====
            conn.commit()

            print("\n" + "="*60)
            print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("="*60)
            print("\n📊 Resumo das mudanças:")
            print("  • Removido: condominio_ids (array)")
            print("  • Adicionado: instagram (VARCHAR 500, nullable)")
            print("  • Adicionado: site (VARCHAR 500, nullable)")
            print("\n✨ Banco de dados sincronizado com código!\n")

            return True

    except Exception as e:
        print("\n" + "="*60)
        print("❌ ERRO NA MIGRAÇÃO!")
        print("="*60)
        print(f"\n🔴 Erro: {str(e)}")
        print("\n💡 Dicas:")
        print("  • Verifique conexão com o banco")
        print("  • Verifique se prestadores table existe")
        print("  • Tente novamente após verificar")
        print()
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
