-- =============================================================================
-- Migration 007: colunas de comparação PuLP
-- =============================================================================

-- consultas: resultado do solver de referência (PuLP/CBC)
ALTER TABLE consultas
    ADD COLUMN IF NOT EXISTS z_pulp          REAL NULL,
    ADD COLUMN IF NOT EXISTS status_lp_pulp  TEXT NULL,
    ADD COLUMN IF NOT EXISTS delta_z_pct     REAL NULL;

-- clusters_resultado: limite calculado pelo PuLP para comparação lado a lado
ALTER TABLE clusters_resultado
    ADD COLUMN IF NOT EXISTS limite_otimizado_pulp INTEGER NULL;

-- =============================================================================
