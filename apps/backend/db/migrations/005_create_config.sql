-- =============================================================================
-- Migration 005: tabela parametros_modelo
-- Armazena os parâmetros padrão do modelo de otimização.
-- Contém sempre exatamente uma linha, atualizada via UPDATE pelo backend.
-- Nomes das colunas entre aspas para preservar o case original dos parâmetros.
-- =============================================================================

CREATE TABLE IF NOT EXISTS parametros_modelo (
    "t"     REAL    NOT NULL,
    "LGD"   REAL    NOT NULL,
    "u_bar" REAL    NOT NULL,
    "L_max" REAL    NOT NULL,
    "T"     REAL    NOT NULL
);

-- =============================================================================