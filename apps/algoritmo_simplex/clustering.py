"""
apps/algoritmo_simplex/clustering.py

Agrupa clientes em clusters por decil de `pd_produto` e calcula os parâmetros
agregados necessários para o modelo de otimização de limites de crédito via Simplex.

A clusterização primária é feita sobre clientes elegíveis (flag_filtros == 0)
em 10 decis de `pd_produto`, alinhados com a calibração gamma_d definida na
Seção 1.5.1 de `artefatos/modelagem_matematica.md`. Para cada cluster, são
calculados os parâmetros que o LP precisa: n_k, PD_k, pi_k, CP_k, m_k e gamma_decil.

Uso:
    python clustering.py <arquivo_clientes.csv> [parametros.json]

Entrada:
    - <nome>.csv: base de clientes no nível individual
    - parametros.json (opcional): arquivo de parâmetros com edges_pd e gamma_decil.
      Se omitido, usa parametros.json padrão.

Saída:
    - <nome>_com_cluster.csv : base original com a coluna cluster_id adicionada
    - <nome>_clusters.csv    : tabela agregada no nível do cluster com parâmetros para o LP

Arquivos CSV devem estar em apps/data/csv/
Arquivos de saída serão gerados em apps/data/csv/
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd


# Faixas de score_credito_cross -> multiplicador m_k (Seção 1.5 da modelagem)
M_K_RANGES = [
    (100, 700, 0.20),
    (700, 800, 0.25),
    (800, 850, 0.30),
    (850, 900, 0.35),
    (900, 960, 0.45),
]


def normalize_propensao(score):
    """Normaliza a propensão para o intervalo [0, 1]"""
    pi = (score.astype(float) - 3.0) / 843.0
    return pi.clip(0.0, 1.0)


def build_cp_proxy(df):
    """Caso não haja a coluna capacidade_pagamento, usa proxy baseado na renda."""
    cp = df["capacidade_pagamento"]
    renda = df["renda_estimada"]
    return cp.where(cp.notna(), renda * 0.30)


def score_to_m(score_cross_mean):
    """Mapeia o score_credito_cross médio do cluster ao multiplicador m_k,
    conforme as cinco faixas definidas na Seção 1.5 da modelagem matemática:
      [100, 700)   -> 0,20
      [700, 800)   -> 0,25
      [800, 850)   -> 0,30
      [850, 900)   -> 0,35
      [900, 960]   -> 0,45
    Valores abaixo de 100 recebem m_k da faixa mais baixa (0,20); valores
    acima de 960 recebem o teto (0,45).
    """
    s = float(score_cross_mean)
    if s < 100:
        return 0.20
    for low, high, m in M_K_RANGES:
        if low <= s < high:
            return m
    return M_K_RANGES[-1][2]


def load_params(json_name):
    """Carrega o JSON de parâmetros (edges_pd, gamma_decil)."""
    if json_name is None:
        json_name = "parametros.json"
    json_path = Path(__file__).resolve().parent / "input" / json_name
    if not json_path.exists():
        raise FileNotFoundError(f"Arquivo de parâmetros não encontrado: {json_path}")
    with open(json_path) as f:
        return json.load(f)


def assign_decil(pd_value, edges):
    """Retorna o índice do decil (0..9) ao qual pd_value pertence, segundo edges_pd."""
    for d in range(10):
        if edges[d] <= pd_value < edges[d + 1]:
            return d
    return 9


def main(input_csv_name, params_json_name=None):
    params = load_params(params_json_name)
    edges_pd = params["edges_pd"]
    gamma_decil = params["gamma_decil"]
    assert len(edges_pd) == 11, "edges_pd deve ter 11 elementos (10 decis)"
    assert len(gamma_decil) == 10, "gamma_decil deve ter 10 elementos"

    input_path = (
        Path(__file__).resolve().parent.parent / "data" / "csv" / input_csv_name
    )
    df = pd.read_csv(input_path)

    # (1) filtra elegíveis
    df = df[df["flag_filtros"] == 0].copy()

    # (2) features derivadas que batem com o LP
    df["pi"] = normalize_propensao(df["score_propensao_contrato"])
    df["cp_proxy"] = build_cp_proxy(df)

    # (3) atribui o decil de pd_produto a cada cliente (0..9)
    df["decil_idx"] = df["pd_produto"].apply(lambda v: assign_decil(float(v), edges_pd))
    df["cluster_id"] = df["decil_idx"].astype(int)

    # (4) agrega e produz os parâmetros do LP
    def p5(x):
        return float(np.nanquantile(x.astype(float), 0.05))

    clusters = df.groupby("cluster_id", as_index=False).agg(
        n_k=("pd_produto", "count"),
        PD_k=("pd_produto", "mean"),
        pi_k=("pi", "mean"),
        CP_k=("cp_proxy", p5),
        score_cross_mean=("score_credito_cross", "mean"),
    )

    # (5) garante presença dos 10 decis: decis sem amostra recebem placeholders neutros
    template = pd.DataFrame({"cluster_id": list(range(10))})
    clusters = template.merge(clusters, on="cluster_id", how="left")
    clusters["n_k"] = clusters["n_k"].fillna(0).astype(int)
    clusters["PD_k"] = clusters["PD_k"].fillna(0.0)
    clusters["pi_k"] = clusters["pi_k"].fillna(0.0)
    clusters["CP_k"] = clusters["CP_k"].fillna(0.0)
    clusters["score_cross_mean"] = clusters["score_cross_mean"].fillna(0.0)

    clusters["m_k"] = clusters["score_cross_mean"].apply(score_to_m)
    clusters["gamma_decil"] = clusters["cluster_id"].apply(
        lambda d: gamma_decil[int(d)]
    )
    clusters["decil"] = clusters["cluster_id"].apply(lambda d: f"D{int(d) + 1}")

    clusters = clusters[
        [
            "cluster_id",
            "decil",
            "n_k",
            "PD_k",
            "pi_k",
            "CP_k",
            "score_cross_mean",
            "m_k",
            "gamma_decil",
        ]
    ]

    # (6) salva saídas com nomes derivados do arquivo de entrada
    out_dir = Path(__file__).resolve().parent.parent / "data" / "csv"
    stem = Path(input_csv_name).stem

    df.to_csv(out_dir / f"{stem}_com_cluster.csv", index=False)
    clusters.to_csv(out_dir / f"{stem}_clusters.csv", index=False)

    print(f"Arquivos salvos em: {out_dir}")
    print(f"  {stem}_com_cluster.csv")
    print(f"  {stem}_clusters.csv")
    print(f"Clusters gerados: {len(clusters)} decis (10 esperados)")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso:")
        print("    python clustering.py <arquivo_clientes.csv> [parametros.json]")
        sys.exit(1)

    csv_name = sys.argv[1]
    json_name = sys.argv[2] if len(sys.argv) > 2 else None
    main(csv_name, json_name)
