-- =============================================================================
-- Migration 001: tabela safras
-- =============================================================================

CREATE TABLE IF NOT EXISTS safras (
    id          TEXT        NOT NULL,
    numero      INTEGER     NOT NULL,
    nome        TEXT        NOT NULL,
    criado_em   TEXT        NOT NULL,

    CONSTRAINT pk_safras PRIMARY KEY (id),
    CONSTRAINT uq_safras_numero UNIQUE (numero),
    CONSTRAINT ck_safras_numero_positivo CHECK (numero >= 1),
    CONSTRAINT ck_safras_nome_formato CHECK (nome LIKE 'M%')
);

-- busca da maior safra existente (usada ao criar nova safra sem numero informado)
CREATE INDEX IF NOT EXISTS idx_safras_numero
    ON safras (numero DESC);

-- =============================================================================