-- =============================================================================
-- Migration 006: seed da tabela parametros_modelo
-- Insere os valores padrão dos parâmetros do modelo de otimização.
-- Executado apenas uma vez - re-execuções não inserem duplicatas.
-- =============================================================================

INSERT INTO parametros_modelo ("t", "LGD", "u_bar", "L_max", "T")
SELECT 0.0175, 0.8, 0.75, 25000.0, 15.0
WHERE NOT EXISTS (SELECT 1 FROM parametros_modelo);

-- =============================================================================