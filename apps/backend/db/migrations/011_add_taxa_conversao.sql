-- =============================================================================
-- Migration 011: taxa de conversão (take-up) como parâmetro editável
-- Ancora o nível absoluto de π na calibração do clustering.
-- Padrão 0.015 (1,5%, fornecido pelo parceiro).
-- =============================================================================

ALTER TABLE parametros_modelo
    ADD COLUMN IF NOT EXISTS taxa_conversao REAL NOT NULL DEFAULT 0.015;

-- =============================================================================
