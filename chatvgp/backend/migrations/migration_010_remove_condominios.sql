-- Migration 010: Remove tabela condominios e coluna logs.condominio_encontrado
-- Condomínios foram removidos do modelo de dados (sem uso no MVP)

ALTER TABLE logs DROP COLUMN IF EXISTS condominio_encontrado;
DROP TABLE IF EXISTS condominios;
