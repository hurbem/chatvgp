-- Migration 009: Remove tabelas de feedback, feedback_links, indicacoes e usuarios
-- Estas funcionalidades foram removidas do MVP (sem uso real até o momento)

DROP TABLE IF EXISTS feedback_links;
DROP TABLE IF EXISTS feedbacks;
DROP TABLE IF EXISTS indicacoes;
DROP TABLE IF EXISTS usuarios;
