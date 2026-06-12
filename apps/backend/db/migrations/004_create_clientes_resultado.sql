-- =============================================================================
-- Migration 004: tabela clientes_resultado
-- =============================================================================
-- Contém apenas clientes elegíveis (flag_filtros == 0), vindos de _com_cluster.parquet.
-- Todos os campos originais do parquet são preservados para rastreabilidade completa,
-- além dos campos derivados pelo pipeline (pd_calibrada, pi_normalizado, cp_proxy)
-- e dos campos de atribuição (segmento_id, limite_otimizado).
-- =============================================================================

CREATE TABLE IF NOT EXISTS clientes_resultado (
    consulta_id                     TEXT        NOT NULL,
    token                           INTEGER     NOT NULL,

    -- campos originais do parquet (todos os elegíveis)
    safra_ref_uso                   TEXT        NOT NULL,
    score_interno                   INTEGER     NOT NULL,
    pd_produto                      REAL        NOT NULL,
    score_generico_1                INTEGER     NULL,       -- ~0.1% nulos
    score_generico_2                INTEGER     NULL,       -- ~0.0% nulos
    capacidade_pagamento            REAL        NULL,       -- até 43% nulos em M2/M3
    delta_capacidade_pagamento      REAL        NULL,       -- mesmo padrão de nulos
    score_propensao_contrato        REAL        NOT NULL,
    score_credito_cross             INTEGER     NOT NULL,
    renda_estimada                  REAL        NULL,       -- ~0.7% nulos
    fx_idade                        TEXT        NOT NULL,
    limite_ofertado                 REAL        NULL,       -- ~97-99% nulos
    flag_contrato                   INTEGER     NOT NULL,
    flag_ativacao                   INTEGER     NOT NULL,
    over30mob3                      INTEGER     NULL,       -- ~100% nulos

    -- campos derivados pelo pipeline
    pd_calibrada                    REAL        NOT NULL,
    pi_normalizado                  REAL        NOT NULL,
    cp_proxy                        REAL        NOT NULL,

    -- atribuição pelo clustering e LP
    segmento_id                      INTEGER     NOT NULL,
    limite_otimizado                INTEGER     NOT NULL,

    CONSTRAINT pk_clientes_resultado
        PRIMARY KEY (consulta_id, token),
    CONSTRAINT fk_clientes_resultado_consulta
        FOREIGN KEY (consulta_id) REFERENCES consultas (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_clientes_resultado_cluster
        FOREIGN KEY (consulta_id, segmento_id)
        REFERENCES clusters_resultado (consulta_id, segmento_id),
    CONSTRAINT ck_clientes_resultado_pd_produto
        CHECK (pd_produto BETWEEN 0 AND 1),
    CONSTRAINT ck_clientes_resultado_pd_calibrada
        CHECK (pd_calibrada BETWEEN 0 AND 1),
    CONSTRAINT ck_clientes_resultado_pi_normalizado
        CHECK (pi_normalizado BETWEEN 0 AND 1),
    CONSTRAINT ck_clientes_resultado_cp_proxy
        CHECK (cp_proxy >= 0),
    CONSTRAINT ck_clientes_resultado_limite
        CHECK (limite_otimizado >= 0),
    CONSTRAINT ck_clientes_resultado_flag_contrato
        CHECK (flag_contrato IN (0, 1)),
    CONSTRAINT ck_clientes_resultado_flag_ativacao
        CHECK (flag_ativacao IN (0, 1))
);

-- histórico de um token específico ao longo das safras
-- (query: "qual foi o limite desse cliente em cada consulta?")
CREATE INDEX IF NOT EXISTS idx_clientes_resultado_token
    ON clientes_resultado (token, consulta_id);

-- todos os clientes de uma consulta com oferta (tela de resultados do front)
CREATE INDEX IF NOT EXISTS idx_clientes_resultado_consulta_ofertados
    ON clientes_resultado (consulta_id, limite_otimizado DESC)
    WHERE limite_otimizado > 0;

-- filtro por cluster dentro de uma consulta (detalhamento de cluster)
CREATE INDEX IF NOT EXISTS idx_clientes_resultado_consulta_cluster
    ON clientes_resultado (consulta_id, segmento_id);

-- análise de risco por consulta (ordenação por pd_calibrada)
CREATE INDEX IF NOT EXISTS idx_clientes_resultado_consulta_pd
    ON clientes_resultado (consulta_id, pd_calibrada ASC);

-- =============================================================================