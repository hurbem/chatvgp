"""
Migration: Adicionar novos campos ao modelo Prestador
- email (UNIQUE)
- cpf_cnpj (UNIQUE)
- descricao (TEXT)
- atualizado_em (DATETIME)
- verificado_hurbem (BOOLEAN)
- indicacoes_moradores (INTEGER)
- premium (BOOLEAN)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__) + "/..")

from sqlalchemy import text
from app.database import engine

def run_migration():
    print("\n" + "="*60)
    print("📋 MIGRATION 002: Adicionar campos ao Prestador")
    print("="*60 + "\n")

    with engine.connect() as connection:
        try:
            # Adicionar coluna email
            print("  ✅ Adicionando: email")
            connection.execute(text(
                "ALTER TABLE prestadores ADD COLUMN IF NOT EXISTS email VARCHAR(255) UNIQUE;"
            ))

            # Adicionar coluna cpf_cnpj
            print("  ✅ Adicionando: cpf_cnpj")
            connection.execute(text(
                "ALTER TABLE prestadores ADD COLUMN IF NOT EXISTS cpf_cnpj VARCHAR(20) UNIQUE;"
            ))

            # Adicionar coluna descricao
            print("  ✅ Adicionando: descricao")
            connection.execute(text(
                "ALTER TABLE prestadores ADD COLUMN IF NOT EXISTS descricao TEXT;"
            ))

            # Adicionar coluna atualizado_em
            print("  ✅ Adicionando: atualizado_em")
            connection.execute(text(
                "ALTER TABLE prestadores ADD COLUMN IF NOT EXISTS atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"
            ))

            # Adicionar coluna verificado_hurbem
            print("  ✅ Adicionando: verificado_hurbem")
            connection.execute(text(
                "ALTER TABLE prestadores ADD COLUMN IF NOT EXISTS verificado_hurbem BOOLEAN DEFAULT FALSE;"
            ))

            # Adicionar coluna indicacoes_moradores
            print("  ✅ Adicionando: indicacoes_moradores")
            connection.execute(text(
                "ALTER TABLE prestadores ADD COLUMN IF NOT EXISTS indicacoes_moradores INTEGER DEFAULT 0;"
            ))

            # Adicionar coluna premium
            print("  ✅ Adicionando: premium")
            connection.execute(text(
                "ALTER TABLE prestadores ADD COLUMN IF NOT EXISTS premium BOOLEAN DEFAULT FALSE;"
            ))

            connection.commit()
            print("\n✅ Migration 002 executada com sucesso!")
            print("="*60 + "\n")

        except Exception as e:
            print(f"\n❌ Erro na migration: {e}")
            print("="*60 + "\n")
            connection.rollback()
            raise

if __name__ == "__main__":
    run_migration()
