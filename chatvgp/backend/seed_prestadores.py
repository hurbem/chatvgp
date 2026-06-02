#!/usr/bin/env python3
"""
Script para inserir dados de teste: 5 prestadores na categoria 1 (Encanador)
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Prestador, Categoria, Condominio, Base

# Configurar banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/chatvgp")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def seed_prestadores():
    """Insere 5 prestadores de encanamento."""
    session = SessionLocal()

    try:
        # Verificar se categoria 1 existe
        categoria = session.query(Categoria).filter(Categoria.id == 1).first()
        if not categoria:
            print("❌ Categoria 1 não encontrada!")
            return

        # Verificar se condominio 2 existe
        condominio = session.query(Condominio).filter(Condominio.id == 2).first()
        if not condominio:
            print("❌ Condomínio 2 não encontrado!")
            return

        # Dados dos 5 prestadores
        prestadores_data = [
            {
                "nome": "Carlos Silva - Encanador",
                "whatsapp": "11987654321",
                "categoria_id": 1,
                "condominio_ids": [2],
                "status": "ativo",
                "notas": "Especialista em hidráulica residencial"
            },
            {
                "nome": "Roberto Santos",
                "whatsapp": "11987654322",
                "categoria_id": 1,
                "condominio_ids": [2],
                "status": "ativo",
                "notas": "Atua há 15 anos na região"
            },
            {
                "nome": "Felipe Oliveira",
                "whatsapp": "11987654323",
                "categoria_id": 1,
                "condominio_ids": [2],
                "status": "ativo",
                "notas": "Reparos urgentes 24h"
            },
            {
                "nome": "Marcelo Costa",
                "whatsapp": "11987654324",
                "categoria_id": 1,
                "condominio_ids": [2],
                "status": "ativo",
                "notas": "Orçamentos sem custo"
            },
            {
                "nome": "André Pereira",
                "whatsapp": "11987654325",
                "categoria_id": 1,
                "condominio_ids": [2],
                "status": "ativo",
                "notas": "Trabalho com garantia"
            }
        ]

        # Inserir prestadores
        count = 0
        for data in prestadores_data:
            # Verificar se já existe
            existing = session.query(Prestador).filter(Prestador.nome == data["nome"]).first()
            if existing:
                print(f"⏭️  {data['nome']} já existe")
                continue

            prestador = Prestador(**data)
            session.add(prestador)
            count += 1

        session.commit()
        print(f"✅ {count} prestadores inseridos com sucesso!")

    except Exception as e:
        session.rollback()
        print(f"❌ Erro: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed_prestadores()
