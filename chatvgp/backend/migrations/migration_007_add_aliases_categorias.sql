-- Migration 007: Adicionar coluna 'aliases' na tabela categorias
-- Armazena palavras-chave/sinônimos usados na busca de categorias

ALTER TABLE categorias
    ADD COLUMN IF NOT EXISTS aliases VARCHAR(500);
