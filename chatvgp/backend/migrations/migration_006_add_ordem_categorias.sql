-- Migration 006: Adicionar coluna 'ordem' na tabela categorias
-- Controla a ordem de apresentação das categorias

ALTER TABLE categorias
    ADD COLUMN IF NOT EXISTS ordem INTEGER DEFAULT 999;

UPDATE categorias SET ordem = (id * 10) WHERE ordem = 999;

CREATE INDEX IF NOT EXISTS idx_categorias_ordem ON categorias(ordem);
