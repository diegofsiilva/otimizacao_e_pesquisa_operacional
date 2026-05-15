"""
apps/algoritmo_simplex/clustering.py

Agrupa clientes em clusters usando K-Means e calcula os parâmetros agregados
necessários para o modelo de otimização de limites de crédito via Simplex.

A clusterização é feita sobre clientes elegíveis (flag_filtros == 0), usando as
features pd_calibrada, capacidade_pagamento, score_credito_cross, score_propensao_contrato
e fx_idade. Para cada cluster, são calculados os parâmetros que o LP precisa:
n_k, PD_k, pi_k, CP_k e m_k.

Uso:
    python clustering.py <arquivo_clientes.csv>

Entrada:
    - <nome>.csv: base de clientes no nível individual (com coluna pd_calibrada)

Saída:
    - <nome>_com_cluster.csv : base original com a coluna cluster_id adicionada
    - <nome>_clusters.csv    : tabela agregada no nível do cluster com parâmetros para o LP

Arquivos CSV devem estar em data/csv/
Arquivos de saída serão gerados em data/csv/
"""

from pathlib import Path
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer


def normalize_propensao(score: pd.Series) -> pd.Series:
    """Normaliza a propensão para o intervalo [0, 1]"""
    pi = (score.astype(float) - 3.0) / 843.0
    return pi.clip(0.0, 1.0)


def build_cp_proxy(df: pd.DataFrame) -> pd.Series:
    """Caso não haja a coluna capacidade_pagamento, usa proxy baseado na renda estimada"""
    cp = df["capacidade_pagamento"]
    renda = df["renda_estimada"]
    return cp.where(cp.notna(), renda * 0.30)


def score_to_m(
    score_cross_mean: float, *, s_low=300.0, s_high=900.0, m_low=0.3, m_high=1.8
) -> float:
    """Calcula o fator de alavancagem m_k do cluster a partir do score de crédito médio."""
    x = (score_cross_mean - s_low) / (s_high - s_low)
    x = float(np.clip(x, 0.0, 1.0))
    return m_low + x * (m_high - m_low)


def main(
    input_csv_name: str,
    n_clusters: int = 7,
    random_state: int = 42,
):
    input_path = (
        Path(__file__).resolve().parent.parent.parent / "data" / "csv" / input_csv_name
    )
    df = pd.read_csv(input_path)

    # (1) filtra elegíveis
    df = df[df["flag_filtros"] == 0].copy()

    # (2) features derivadas que batem com o LP
    df["pi"] = normalize_propensao(df["score_propensao_contrato"])
    df["cp_proxy"] = build_cp_proxy(df)

    # (3) define colunas para clusterização
    numeric_features = ["pd_calibrada", "cp_proxy", "score_credito_cross", "pi"]
    categorical_features = ["fx_idade"]

    pre = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric_features,
            ),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init="auto")

    pipe = Pipeline([("pre", pre), ("kmeans", model)])
    df["cluster_id"] = pipe.fit_predict(df)

    # (4) agrega e produz os parâmetros do LP
    def p5(x):
        return float(np.nanquantile(x.astype(float), 0.05))

    clusters = df.groupby("cluster_id", as_index=False).agg(
        n_k=("token", "count"),
        PD_k=("pd_calibrada", "mean"),
        pi_k=("pi", "mean"),
        CP_k=("cp_proxy", p5),
        score_cross_mean=("score_credito_cross", "mean"),
    )
    clusters["m_k"] = clusters["score_cross_mean"].apply(score_to_m)

    # (5) salva saídas com nomes derivados do arquivo de entrada
    out_dir = Path(__file__).resolve().parent.parent.parent / "data" / "csv"
    stem = Path(input_csv_name).stem

    df.to_csv(out_dir / f"{stem}_com_cluster.csv", index=False)
    clusters.to_csv(out_dir / f"{stem}_clusters.csv", index=False)

    print(f"Arquivos salvos em: {out_dir}")
    print(f"  {stem}_com_cluster.csv")
    print(f"  {stem}_clusters.csv")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso:")
        print("    python clustering.py <arquivo_clientes.csv>")
        sys.exit(1)

    main(sys.argv[1])
