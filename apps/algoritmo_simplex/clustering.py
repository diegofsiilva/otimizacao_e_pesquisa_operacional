"""
Script para a clusterização da base de dados usando K-means
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

