-- ============================================================
-- Migration 999: Recriação/correção completa do schema (idempotente)
-- ============================================================
-- Objetivo: garantir que o banco de produção (Render Postgres)
-- tenha exatamente as tabelas e colunas usadas pelos models atuais
-- (app/models/*.py), independente de quais migrações incrementais
-- já foram aplicadas.
--
-- Seguro para rodar em um banco já existente: usa
-- CREATE TABLE IF NOT EXISTS e ADD COLUMN IF NOT EXISTS.
--
-- Como executar no Render:
--   1. Dashboard -> chatvgp-api -> Shell (ou conecte via psql usando
--      a "External Database URL" do Render Postgres)
--   2. psql "$DATABASE_URL" -f migration_999_fix_producao_completo.sql
-- ============================================================

-- ---------------------------------------------------------
-- Tabela: categorias
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS categorias (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    aliases VARCHAR(500),
    ordem INTEGER NOT NULL DEFAULT 999
);

CREATE INDEX IF NOT EXISTS ix_categorias_nome ON categorias (nome);

-- Colunas adicionadas em migrações incrementais (caso a tabela já existisse)
ALTER TABLE categorias ADD COLUMN IF NOT EXISTS aliases VARCHAR(500);
ALTER TABLE categorias ADD COLUMN IF NOT EXISTS ordem INTEGER NOT NULL DEFAULT 999;


-- ---------------------------------------------------------
-- Tabela: prestadores
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS prestadores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    whatsapp VARCHAR(20) NOT NULL UNIQUE,
    cpf_cnpj VARCHAR(20) UNIQUE,
    descricao TEXT,
    instagram VARCHAR(500),
    site VARCHAR(500),
    verificado_hurbem BOOLEAN DEFAULT FALSE,
    premium BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'ativo',
    criado_em TIMESTAMP DEFAULT now(),
    atualizado_em TIMESTAMP DEFAULT now(),
    notas TEXT
);

CREATE INDEX IF NOT EXISTS ix_prestadores_nome ON prestadores (nome);
CREATE INDEX IF NOT EXISTS ix_prestadores_email ON prestadores (email);
CREATE INDEX IF NOT EXISTS ix_prestadores_whatsapp ON prestadores (whatsapp);
CREATE INDEX IF NOT EXISTS ix_prestadores_cpf_cnpj ON prestadores (cpf_cnpj);
CREATE INDEX IF NOT EXISTS ix_prestadores_status ON prestadores (status);

-- Colunas adicionadas em migrações incrementais (caso a tabela já existisse)
ALTER TABLE prestadores ADD COLUMN IF NOT EXISTS email VARCHAR(255);
ALTER TABLE prestadores ADD COLUMN IF NOT EXISTS cpf_cnpj VARCHAR(20);
ALTER TABLE prestadores ADD COLUMN IF NOT EXISTS descricao TEXT;
ALTER TABLE prestadores ADD COLUMN IF NOT EXISTS instagram VARCHAR(500);
ALTER TABLE prestadores ADD COLUMN IF NOT EXISTS site VARCHAR(500);
ALTER TABLE prestadores ADD COLUMN IF NOT EXISTS verificado_hurbem BOOLEAN DEFAULT FALSE;
ALTER TABLE prestadores ADD COLUMN IF NOT EXISTS premium BOOLEAN DEFAULT FALSE;
ALTER TABLE prestadores ADD COLUMN IF NOT EXISTS notas TEXT;
ALTER TABLE prestadores ADD COLUMN IF NOT EXISTS atualizado_em TIMESTAMP DEFAULT now();


-- ---------------------------------------------------------
-- Tabela: prestador_categorias (associação N:N)
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS prestador_categorias (
    id SERIAL PRIMARY KEY,
    prestador_id INTEGER NOT NULL REFERENCES prestadores(id),
    categoria_id INTEGER NOT NULL REFERENCES categorias(id),
    CONSTRAINT uq_prestador_categoria UNIQUE (prestador_id, categoria_id)
);

CREATE INDEX IF NOT EXISTS ix_prestador_categorias_prestador_id ON prestador_categorias (prestador_id);
CREATE INDEX IF NOT EXISTS ix_prestador_categorias_categoria_id ON prestador_categorias (categoria_id);


-- ---------------------------------------------------------
-- Tabela: logs
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(100),
    pergunta TEXT,
    categoria_encontrada VARCHAR(255),
    mensagem TEXT,
    criado_em TIMESTAMP DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_logs_tipo ON logs (tipo);
CREATE INDEX IF NOT EXISTS ix_logs_criado_em ON logs (criado_em);


-- ============================================================
-- Fim da migration 999
-- ============================================================
