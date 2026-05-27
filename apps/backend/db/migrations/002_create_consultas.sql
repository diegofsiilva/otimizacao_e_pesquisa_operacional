-- =============================================================================
-- Migration 002: tabela consultas
-- =============================================================================

CREATE TABLE IF NOT EXISTS consultas (
    id                      TEXT        NOT NULL,
    safra_id                TEXT        NOT NULL,
    nome_arquivo_parquet    TEXT        NOT NULL,
    parametros              TEXT        NOT NULL,   -- JSON serializado

    -- estado do processo assíncrono
    status_consulta         TEXT        NOT NULL    DEFAULT 'pendente',

    -- estado interno do algoritmo Simplex (preenchido ao concluir)
    status_lp               TEXT        NULL,

    -- resultado da otimização
    z_otimo                 REAL        NULL,

    -- contagens (preenchidas ao concluir)
    n_clientes_total        INTEGER     NULL,
    n_clientes_elegiveis    INTEGER     NULL,
    n_clientes_ofertados    INTEGER     NULL,
    n_clusters              INTEGER     NULL,

    -- timestamps do ciclo de vida
    criado_em               TEXT        NOT NULL,
    iniciado_em             TEXT        NULL,
    concluido_em            TEXT        NULL,

    -- diagnóstico de erros
    erro_etapa              TEXT        NULL,       -- calibracao | clustering | otimizacao
    erro_mensagem           TEXT        NULL,

    CONSTRAINT pk_consultas PRIMARY KEY (id),
    CONSTRAINT fk_consultas_safra
        FOREIGN KEY (safra_id) REFERENCES safras (id),
    CONSTRAINT ck_consultas_status_consulta CHECK (
        status_consulta IN ('pendente', 'executando', 'concluido', 'erro')
    ),
    CONSTRAINT ck_consultas_status_lp CHECK (
        status_lp IS NULL
        OR status_lp IN ('otimo', 'multiplas_solucoes')
    ),
    CONSTRAINT ck_consultas_erro_etapa CHECK (
        erro_etapa IS NULL
        OR erro_etapa IN ('calibracao', 'clustering', 'otimizacao')
    ),
    CONSTRAINT ck_consultas_z_otimo CHECK (
        z_otimo IS NULL OR z_otimo >= 0
    ),
    CONSTRAINT ck_consultas_n_positivos CHECK (
        (n_clientes_total    IS NULL OR n_clientes_total    >= 0) AND
        (n_clientes_elegiveis IS NULL OR n_clientes_elegiveis >= 0) AND
        (n_clientes_ofertados IS NULL OR n_clientes_ofertados >= 0) AND
        (n_clusters          IS NULL OR n_clusters          >= 0)
    ),
    -- erro_etapa e erro_mensagem devem estar presentes juntos
    CONSTRAINT ck_consultas_erro_consistente CHECK (
        (erro_etapa IS NULL) = (erro_mensagem IS NULL)
    )
);

-- listagem cronológica (tela principal do front)
CREATE INDEX IF NOT EXISTS idx_consultas_criado_em
    ON consultas (criado_em DESC);

-- filtro por safra (listar todas as consultas de uma safra)
CREATE INDEX IF NOT EXISTS idx_consultas_safra_id
    ON consultas (safra_id, criado_em DESC);

-- filtro por status (fila de jobs pendentes no backend)
CREATE INDEX IF NOT EXISTS idx_consultas_status_consulta
    ON consultas (status_consulta)
    WHERE status_consulta IN ('pendente', 'executando');

-- =============================================================================