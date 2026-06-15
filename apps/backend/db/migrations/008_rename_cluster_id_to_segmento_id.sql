-- =============================================================================
-- Migration 008: renomeia cluster_id -> segmento_id
-- Necessário para bancos criados antes do refactor de 67abbfc.
-- Usa bloco DO para rodar só se a coluna antiga ainda existir.
-- =============================================================================

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'clusters_resultado' AND column_name = 'cluster_id'
    ) THEN
        -- remove FK de clientes_resultado que aponta para clusters_resultado(cluster_id)
        ALTER TABLE clientes_resultado
            DROP CONSTRAINT IF EXISTS fk_clientes_resultado_cluster;

        -- remove índices que referenciam cluster_id
        DROP INDEX IF EXISTS idx_clusters_resultado_consulta_cluster;

        -- renomeia em clusters_resultado
        ALTER TABLE clusters_resultado RENAME COLUMN cluster_id TO segmento_id;

        -- renomeia em clientes_resultado (se também tiver cluster_id)
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'clientes_resultado' AND column_name = 'cluster_id'
        ) THEN
            ALTER TABLE clientes_resultado RENAME COLUMN cluster_id TO segmento_id;
        END IF;

        -- recria índice
        CREATE INDEX IF NOT EXISTS idx_clusters_resultado_consulta_cluster
            ON clusters_resultado (consulta_id, segmento_id ASC);

        -- recria FK
        ALTER TABLE clientes_resultado
            ADD CONSTRAINT fk_clientes_resultado_cluster
            FOREIGN KEY (consulta_id, segmento_id)
            REFERENCES clusters_resultado (consulta_id, segmento_id);
    END IF;
END $$;
