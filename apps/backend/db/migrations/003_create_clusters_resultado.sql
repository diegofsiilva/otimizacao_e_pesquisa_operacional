-- =============================================================================
-- Migration 003: tabela clusters_resultado
-- =============================================================================

CREATE TABLE IF NOT EXISTS clusters_resultado (
    id                          INTEGER  GENERATED ALWAYS AS IDENTITY, -- ROWID / autoincrement
    consulta_id                 TEXT        NOT NULL,
    segmento_id                  INTEGER     NOT NULL,   -- 0 a K-1

    -- parâmetros agregados do cluster (vindos de _clusters.parquet)
    n_clientes                  INTEGER     NOT NULL,
    pd_media                    REAL        NOT NULL,
    pi_media                    REAL        NOT NULL,
    cp_percentil5               REAL        NOT NULL,
    score_credito_cross_medio   REAL        NOT NULL,
    ck_medio                    REAL        NOT NULL,
    fator_alavancagem           REAL        NOT NULL,

    -- resultado do LP para este cluster
    limite_otimizado            INTEGER     NOT NULL,

    CONSTRAINT pk_clusters_resultado PRIMARY KEY (id),
    CONSTRAINT fk_clusters_resultado_consulta
        FOREIGN KEY (consulta_id) REFERENCES consultas (id)
        ON DELETE CASCADE,
    CONSTRAINT uq_clusters_resultado_consulta_cluster
        UNIQUE (consulta_id, segmento_id),
    CONSTRAINT ck_clusters_resultado_n_clientes CHECK (n_clientes > 0),
    CONSTRAINT ck_clusters_resultado_pd_media CHECK (pd_media BETWEEN 0 AND 1),
    CONSTRAINT ck_clusters_resultado_pi_media CHECK (pi_media BETWEEN 0 AND 1),
    CONSTRAINT ck_clusters_resultado_cp_percentil5 CHECK (cp_percentil5 >= 0),
    CONSTRAINT ck_clusters_resultado_fator_alavancagem CHECK (fator_alavancagem > 0),
    CONSTRAINT ck_clusters_resultado_limite CHECK (limite_otimizado >= 0),
    CONSTRAINT ck_clusters_resultado_segmento_id CHECK (segmento_id >= 0)
);

-- leitura do resultado de uma consulta ordenada por cluster (resposta ao front)
CREATE INDEX IF NOT EXISTS idx_clusters_resultado_consulta_cluster
    ON clusters_resultado (consulta_id, segmento_id ASC);

-- ranking de clusters por limite (análise de distribuição)
CREATE INDEX IF NOT EXISTS idx_clusters_resultado_consulta_limite
    ON clusters_resultado (consulta_id, limite_otimizado DESC);

-- =============================================================================