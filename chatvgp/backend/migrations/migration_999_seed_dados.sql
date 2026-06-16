-- ============================================================
-- Seed de dados iniciais (idempotente - usa ON CONFLICT DO NOTHING)
-- ============================================================
-- Rode DEPOIS de migration_999_fix_producao_completo.sql
--   psql "$DATABASE_URL" -f migration_999_seed_dados.sql
--
-- Ajuste/complete a lista de categorias e aliases conforme
-- as categorias já cadastradas em produção (via /api/categorias).
-- ============================================================

-- ---------------------------------------------------------
-- Categorias (com aliases para o keyword matching do chat)
-- ---------------------------------------------------------
INSERT INTO categorias (nome, descricao, aliases, ordem) VALUES
    ('Encanador', 'Serviços de hidráulica e encanamento', 'encanamento,hidraulica,vazamento,cano,torneira,registro', 1),
    ('Eletricista', 'Serviços elétricos residenciais', 'eletrica,fiacao,disjuntor,tomada,curto,instalacao eletrica', 2),
    ('Pintor', 'Pintura residencial e predial', 'pintura,pintar,parede,textura,grafiato', 3),
    ('Pedreiro', 'Alvenaria, reformas e construção', 'reforma,alvenaria,construcao,obra,reboco', 4),
    ('Diarista', 'Limpeza residencial', 'limpeza,faxina,domestica,arrumacao', 5),
    ('Jardineiro', 'Manutenção de jardins e quintais', 'jardim,jardinagem,grama,poda,paisagismo', 6),
    ('Marceneiro', 'Móveis planejados e marcenaria', 'moveis,marcenaria,armario,madeira', 7),
    ('Chaveiro', 'Chaves, fechaduras e segredos', 'chave,fechadura,segredo,trava', 8)
ON CONFLICT (nome) DO NOTHING;


-- ---------------------------------------------------------
-- Prestadores de exemplo (categoria "Encanador")
-- Equivalente ao seed_prestadores.py
-- ---------------------------------------------------------
INSERT INTO prestadores (nome, whatsapp, status, notas) VALUES
    ('Carlos Silva - Encanador', '11987654321', 'ativo', 'Especialista em hidráulica residencial'),
    ('Roberto Santos', '11987654322', 'ativo', 'Atua há 15 anos na região'),
    ('Felipe Oliveira', '11987654323', 'ativo', 'Reparos urgentes 24h'),
    ('Marcelo Costa', '11987654324', 'ativo', 'Orçamentos sem custo'),
    ('André Pereira', '11987654325', 'ativo', 'Trabalho com garantia')
ON CONFLICT (whatsapp) DO NOTHING;

-- Vincula os prestadores acima à categoria "Encanador"
INSERT INTO prestador_categorias (prestador_id, categoria_id)
SELECT p.id, c.id
FROM prestadores p
JOIN categorias c ON c.nome = 'Encanador'
WHERE p.whatsapp IN ('11987654321', '11987654322', '11987654323', '11987654324', '11987654325')
ON CONFLICT (prestador_id, categoria_id) DO NOTHING;

-- ============================================================
-- Fim do seed
-- ============================================================
