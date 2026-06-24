-- =============================================================================
-- Migration 009: atualiza o horizonte T padrão de 22 para 15 meses
-- Bancos já semeados pela migration 006 com T = 22 passam a usar 15.
-- Só altera a linha se ela ainda estiver no antigo padrão (22), preservando
-- qualquer valor que o usuário tenha ajustado manualmente.
-- =============================================================================

UPDATE parametros_modelo SET "T" = 15.0 WHERE "T" = 22.0;

-- =============================================================================
