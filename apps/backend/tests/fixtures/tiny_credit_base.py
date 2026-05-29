from __future__ import annotations

from pathlib import Path


def criar_tiny_credit_base(destino: Path) -> Path:
    """
    Gera um parquet minimo com o esquema esperado pelo front/back.

    Este fixture e usado como base pequena para testes manuais de upload e para
    evoluir testes end-to-end completos sem depender das safras reais do parceiro.
    """
    import pandas as pd

    destino.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(
        [
            {
                "token": 1,
                "safra_ref_uso": "M1",
                "flag_filtros": 0,
                "score_interno": 820,
                "pd_produto": 0.02,
                "score_generico_1": 800,
                "score_generico_2": 790,
                "capacidade_pagamento": 1200.0,
                "delta_capacidade_pagamento": 0.0,
                "score_propensao_contrato": 650.0,
                "score_credito_cross": 720,
                "renda_estimada": 6000.0,
                "fx_idade": "26-35",
                "limite_ofertado": None,
                "flag_contrato": 1,
                "flag_ativacao": 1,
                "over30mob3": None,
            },
            {
                "token": 2,
                "safra_ref_uso": "M1",
                "flag_filtros": 0,
                "score_interno": 700,
                "pd_produto": 0.05,
                "score_generico_1": 710,
                "score_generico_2": 705,
                "capacidade_pagamento": 850.0,
                "delta_capacidade_pagamento": -50.0,
                "score_propensao_contrato": 420.0,
                "score_credito_cross": 660,
                "renda_estimada": 4200.0,
                "fx_idade": "36-45",
                "limite_ofertado": None,
                "flag_contrato": 0,
                "flag_ativacao": 1,
                "over30mob3": None,
            },
            {
                "token": 3,
                "safra_ref_uso": "M1",
                "flag_filtros": 1,
                "score_interno": 500,
                "pd_produto": 0.2,
                "score_generico_1": 520,
                "score_generico_2": 510,
                "capacidade_pagamento": 300.0,
                "delta_capacidade_pagamento": -100.0,
                "score_propensao_contrato": 100.0,
                "score_credito_cross": 540,
                "renda_estimada": 1800.0,
                "fx_idade": "46-55",
                "limite_ofertado": None,
                "flag_contrato": 0,
                "flag_ativacao": 0,
                "over30mob3": None,
            },
        ]
    )
    df.to_parquet(destino, index=False)
    return destino


if __name__ == "__main__":
    criar_tiny_credit_base(Path(__file__).with_name("tiny_credit_base.parquet"))
