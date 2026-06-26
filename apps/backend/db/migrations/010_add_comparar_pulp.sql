-- =============================================================================
-- Migration 010: flag de comparação com o solver de referência (PuLP)
-- Adiciona a coluna comparar_pulp à tabela de parâmetros do modelo.
-- Padrão FALSE: o pipeline NÃO roda o PuLP por padrão (rodar um segundo solver
-- dobra o tempo). A tela de configurações liga/desliga essa validação cruzada.
-- =============================================================================

ALTER TABLE parametros_modelo
    ADD COLUMN IF NOT EXISTS comparar_pulp BOOLEAN NOT NULL DEFAULT false;

-- =============================================================================
