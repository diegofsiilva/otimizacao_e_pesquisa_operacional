"""
apps/algoritmo_simplex/clustering.py
Realiza a clusterização da base de clientes usando K-Means para gerar os parâmetros
necessários para o LP/Simplex (por cluster).

Entrada:
    - CSV com dados dos clientes (ex: base_ref_M1_v2.csv)

Saída:
    - clientes_com_cluster.csv: base no nível do cliente com a coluna cluster_id
    - parametros_cluster.csv: tabela no nível do cluster com parâmetros para o LP

Uso:
    python clustering.py

Arquivos CSV devem estar em apps/data/csv/
Arquivos de saída serão gerados em apps/data/csv/

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
    """Normaliza a propensão para o intervao [0, 1]"""
    pi = (score.astype(float) - 3.0) / 843.0
    return pi.clip(0.0, 1.0)

def build_cp_proxy(df: pd.DataFrame) -> pd.Series:
    """Caso não haja a coluna "capacidade_pagamento", proxy feito com a renda estimada é utilizada"""
    cp = df["capacidade_pagamento"]
    renda = df["renda_estimada"]
    return cp.where(cp.notna(), renda * 0.30)

def score_to_m(score_cross_mean: float, *, s_low=300.0, s_high=900.0, m_low=0.3, m_high=1.8) -> float:
    """Cálculo da média de propensão para o cluster"""
    x = (score_cross_mean - s_low) / (s_high - s_low)
    x = float(np.clip(x, 0.0, 1.0))
    return m_low + x * (m_high - m_low)

def main(
    input_csv_name: str = "base_ref_M1_v2.csv",
    n_clusters: int = 7,
    random_state: int = 42,
):
    input_path = Path(__file__).resolve().parent.parent / "data" / "csv" / input_csv_name
    df = pd.read_csv(input_path)

    # (1) filtra elegíveis
    df = df[df["flag_filtros"] == 0].copy()

    # (2) features derivadas que batem com o LP
    df["pi"] = normalize_propensao(df["score_propensao_contrato"])
    df["cp_proxy"] = build_cp_proxy(df)

    # (3) define colunas para clusterização
    numeric_features = ["pd_produto", "cp_proxy", "score_credito_cross", "pi"]
    categorical_features = ["fx_idade"]

    pre = ColumnTransformer(
        transformers=[
            ("num", Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init="auto")

    pipe = Pipeline([("pre", pre), ("kmeans", model)])
    df["cluster_id"] = pipe.fit_predict(df)

    # (4) agrega e produz os parâmetros do LP
    def p5(x):
        return float(np.nanquantile(x.astype(float), 0.05))

    clusters = (
        df.groupby("cluster_id", as_index=False)
          .agg(
              n_k=("token", "count"),
              PD_k=("pd_produto", "mean"),
              pi_k=("pi", "mean"),
              CP_k=("cp_proxy", p5),
              score_cross_mean=("score_credito_cross", "mean"),
          )
    )
    clusters["m_k"] = clusters["score_cross_mean"].apply(score_to_m)

    # (5) salva saídas
    out_dir = Path(__file__).resolve().parent.parent / "data" / "csv"
    df.to_csv(out_dir / "clientes_com_cluster.csv", index=False)
    clusters.to_csv(out_dir / "parametros_cluster.csv", index=False)

    print("OK")
    print("clientes_com_cluster.csv e parametros_cluster.csv gerados em apps/data/csv/")

if __name__ == "__main__":
    main()