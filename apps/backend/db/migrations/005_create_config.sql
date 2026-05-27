-- =============================================================================
-- Migration 005: tabela config
-- Armazena os parâmetros padrão do modelo de otimização.
-- Contém sempre exatamente uma linha, atualizada via UPDATE pelo backend.
-- =============================================================================

CREATE TABLE IF NOT EXISTS config (
    t       REAL    NOT NULL,
    LGD     REAL    NOT NULL,
    u_bar   REAL    NOT NULL,
    L_max   REAL    NOT NULL,
    T       REAL    NOT NULL
);

-- =============================================================================