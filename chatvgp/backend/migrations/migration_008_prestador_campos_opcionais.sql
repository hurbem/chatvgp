-- Migration 008: Tornar email e cpf_cnpj opcionais na tabela prestadores

ALTER TABLE prestadores ALTER COLUMN email DROP NOT NULL;
ALTER TABLE prestadores ALTER COLUMN cpf_cnpj DROP NOT NULL;
