from __future__ import annotations

import math
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from db.storage import UPLOAD_DIR, ensure_dirs, load_params, load_state, read_dataframe, save_params, save_state
from model.schemas import (
    Cluster,
    DashboardKPIs,
    DashboardResponse,
    GeracaoLimitesResponse,
    GeracaoResumo,
    LimiteCluster,
    ParametrosModelo,
    ResultadosKPIs,
    ResultadosResponse,
    SeriePonto,
    StatusDistribuicao,
)


ALGORITMO_DIR = Path(__file__).resolve().parents[2] / "algoritmo_simplex"
if str(ALGORITMO_DIR) not in sys.path:
    sys.path.append(str(ALGORITMO_DIR))

from models import Problema  # noqa: E402
from simplex import simplex  # noqa: E402


REQUIRED_COLUMNS = {
    "flag_filtros",
    "pd_calibrada",
    "score_propensao_contrato",
    "capacidade_pagamento",
    "renda_estimada",
    "score_credito_cross",
    "fx_idade",
}


def _dump_model(model: Any) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump(mode="json")
    return _jsonable(model.dict())


def _jsonable(value: Any) -> Any:
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    return value


def _money(value: float | int | None) -> float | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    return round(float(value), 2)


def _normalize_propensao(score: pd.Series) -> pd.Series:
    pi = (score.astype(float) - 3.0) / 843.0
    return pi.clip(0.0, 1.0)


def _build_cp_proxy(df: pd.DataFrame) -> pd.Series:
    cp = df["capacidade_pagamento"]
    renda = df["renda_estimada"]
    return cp.where(cp.notna(), renda * 0.30)


def _score_to_m(score_cross_mean: float, s_low: float = 300.0, s_high: float = 900.0) -> float:
    x = (score_cross_mean - s_low) / (s_high - s_low)
    x = float(np.clip(x, 0.0, 1.0))
    return 0.3 + x * (1.8 - 0.3)


def _cluster_id(row: pd.Series, index: int) -> str:
    for column in ["cluster_id", "id_cluster", "token"]:
        if column in row and pd.notna(row[column]):
            return str(row[column])
    return f"CLI-{index + 1:03d}"


def _status_from_row(row: pd.Series) -> str:
    if "status" in row and pd.notna(row["status"]):
        return str(row["status"])
    if "flag_filtros" in row and pd.notna(row["flag_filtros"]):
        return "Ativo" if int(row["flag_filtros"]) == 0 else "Inativo"
    return "Ativo"


def _date_from_index(index: int) -> date:
    return date.today() - timedelta(days=index * 17)


def _validate_columns(df: pd.DataFrame) -> None:
    missing = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing:
        raise ValueError(f"Base sem colunas obrigatorias: {', '.join(missing)}")


def _clusters_from_df(df: pd.DataFrame, limit: int = 50) -> list[Cluster]:
    clusters: list[Cluster] = []
    for position, (_, row) in enumerate(df.head(limit).iterrows()):
        cluster = row.get("cluster_id", row.get("cluster", None))
        limite = row.get("limite_sugerido", row.get("limite", None))
        cadastro = row.get("cadastro", None)
        score = row.get("score_credito_cross", row.get("score", None))
        clusters.append(
            Cluster(
                id_=_cluster_id(row, position),
                cluster=f"CLU-{int(cluster) + 1:03d}" if pd.notna(cluster) else None,
                score=float(score) if pd.notna(score) else None,
                status=_status_from_row(row),
                limite=_money(limite),
                cadastro=pd.to_datetime(cadastro).date() if pd.notna(cadastro) else _date_from_index(position),
            )
        )
    return clusters


def _build_clusters(df: pd.DataFrame, n_clusters: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    from sklearn.cluster import KMeans
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    eligible = df[df["flag_filtros"] == 0].copy()
    if eligible.empty:
        raise ValueError("A base nao possui clusters elegiveis para gerar limites.")

    n_clusters = min(n_clusters, len(eligible))
    eligible["pi"] = _normalize_propensao(eligible["score_propensao_contrato"])
    eligible["cp_proxy"] = _build_cp_proxy(eligible)

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
                ["pd_calibrada", "cp_proxy", "score_credito_cross", "pi"],
            ),
            ("cat", OneHotEncoder(handle_unknown="ignore"), ["fx_idade"]),
        ]
    )
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    pipe = Pipeline([("pre", pre), ("kmeans", model)])
    eligible["cluster_id"] = pipe.fit_predict(eligible)

    def p5(values: pd.Series) -> float:
        return float(np.nanquantile(values.astype(float), 0.05))

    clusters = eligible.groupby("cluster_id", as_index=False).agg(
        n_k=("score_credito_cross", "count"),
        PD_k=("pd_calibrada", "mean"),
        pi_k=("pi", "mean"),
        CP_k=("cp_proxy", p5),
        score_cross_mean=("score_credito_cross", "mean"),
    )
    clusters["m_k"] = clusters["score_cross_mean"].apply(_score_to_m)
    return eligible, clusters.sort_values("cluster_id").reset_index(drop=True)


def _calcular_pd_fin_atual(df: pd.DataFrame) -> float:
    return float(df[df["flag_filtros"] == 0]["pd_calibrada"].mean())


def _montar_problema(clusters: pd.DataFrame, params: dict[str, Any], pd_fin_atual: float) -> Problema:
    t = params["t"]
    lgd = params["LGD"]
    u_bar = params["u_bar"]
    l_max = params["L_max"]

    c = [
        float(row["n_k"] * row["pi_k"] * (u_bar * t * 22 - row["PD_k"] * lgd))
        for _, row in clusters.iterrows()
    ]

    matrix = [[float(row["n_k"] * (row["PD_k"] - pd_fin_atual)) for _, row in clusters.iterrows()]]
    bounds = [0.0]

    for index, row in clusters.iterrows():
        line = [0.0] * len(clusters)
        line[index] = 1.0
        matrix.append(line)
        bounds.append(float(row["m_k"] * row["CP_k"]))

    for index, _ in clusters.iterrows():
        line = [0.0] * len(clusters)
        line[index] = 1.0
        matrix.append(line)
        bounds.append(float(l_max))

    return Problema(c=c, A=matrix, b=bounds)


def get_parametros() -> ParametrosModelo:
    data = load_params()
    state = load_state()
    data["n_clusters"] = state.get("n_clusters", 7)
    return ParametrosModelo(**data)


def update_parametros(payload: ParametrosModelo) -> ParametrosModelo:
    data = _dump_model(payload)
    save_params({key: value for key, value in data.items() if key != "n_clusters"})
    state = load_state()
    state["n_clusters"] = payload.n_clusters
    save_state(state)
    return payload


def save_upload(filename: str, content: bytes) -> Path:
    ensure_dirs()
    target = UPLOAD_DIR / Path(filename).name
    target.write_bytes(content)
    return target


def gerar_limites(path: Path, n_clusters: int | None = None) -> GeracaoLimitesResponse:
    df = read_dataframe(path)
    _validate_columns(df)
    params = get_parametros()
    if n_clusters is not None:
        params.n_clusters = n_clusters

    eligible, clusters = _build_clusters(df, params.n_clusters)
    params_data = _dump_model(params)
    problema = _montar_problema(
        clusters,
        {key: value for key, value in params_data.items() if key != "n_clusters"},
        _calcular_pd_fin_atual(df),
    )
    x, _, status = simplex(problema)

    limites: list[LimiteCluster] = []
    limit_by_cluster: dict[int, float | None] = {}
    for index, row in clusters.iterrows():
        raw_limit = x[index]
        limite = 50 * round(raw_limit / 50) if raw_limit >= 200 else 0
        viable = status in {"otimo", "multiplas_solucoes"} and limite > 0
        final_limit = _money(limite) if viable else None
        cluster_id = int(row["cluster_id"])
        limit_by_cluster[cluster_id] = final_limit
        limites.append(
            LimiteCluster(
                cluster_id=f"CLU-{cluster_id + 1:03d}",
                limite_sugerido=final_limit,
                status="Solucao Viavel" if viable else "Sem Solucao",
                clusters=int(row["n_k"]),
            )
        )

    eligible["limite_sugerido"] = eligible["cluster_id"].map(limit_by_cluster)
    resumo = GeracaoResumo(
        total_clusters=len(limites),
        com_solucao_viavel=sum(1 for item in limites if item.status == "Solucao Viavel"),
        sem_solucao=sum(1 for item in limites if item.status == "Sem Solucao"),
    )
    result = GeracaoLimitesResponse(arquivo=path.name, resumo=resumo, limites=limites)

    state = load_state()
    state["last_upload"] = str(path)
    state["last_result"] = _dump_model(result)
    state["clusters"] = [_dump_model(item) for item in _clusters_from_df(eligible, limit=100)]
    state["n_clusters"] = params.n_clusters
    save_state(state)
    return result


def get_dashboard() -> DashboardResponse:
    state = load_state()
    clusters = [Cluster(**item) for item in state.get("clusters", [])]
    if not clusters:
        clusters = _sample_clusters()
    ativos = sum(1 for item in clusters if item.status == "Ativo")
    limite_total = sum(item.limite or 0 for item in clusters)
    aprovados = sum(1 for item in clusters if (item.limite or 0) > 0)
    taxa = (aprovados / len(clusters) * 100) if clusters else 0
    return DashboardResponse(
        kpis=DashboardKPIs(
            total_clusters=len(clusters),
            clusters_ativos=ativos,
            limite_total=_money(limite_total) or 0,
            taxa_aprovacao=round(taxa, 2),
        ),
        clusters=clusters,
    )


def list_cluster(q: str | None = None, status: str | None = None) -> list[Cluster]:
    clusters = get_dashboard().clusters
    if q:
        normalized = q.lower()
        clusters = [
            item
            for item in clusters
            if normalized in item.id_.lower()
            or (item.cluster is not None and normalized in item.cluster.lower())
        ]
    if status:
        clusters = [item for item in clusters if item.status == status]
    return clusters


def upsert_cluster(payload: Cluster) -> Cluster:
    state = load_state()
    clusters = [Cluster(**item) for item in state.get("clusters", [])]
    found = False
    for index, cluster in enumerate(clusters):
        if cluster.id_ == payload.id_:
            clusters[index] = payload
            found = True
            break
    if not found:
        clusters.append(payload)
    state["clusters"] = [_dump_model(item) for item in clusters]
    save_state(state)
    return payload


def delete_cluster(cluster_id: str) -> bool:
    state = load_state()
    clusters = [Cluster(**item) for item in state.get("clusters", [])]
    remaining = [item for item in clusters if item.id_ != cluster_id]
    if len(remaining) == len(clusters):
        return False
    state["clusters"] = [_dump_model(item) for item in remaining]
    save_state(state)
    return True


def get_resultados() -> ResultadosResponse:
    state = load_state()
    last_result: dict[str, Any] | None = state.get("last_result")
    limites = [LimiteCluster(**item) for item in last_result["limites"]] if last_result else _sample_limites()

    clusters_viaveis = sum(item.clusters for item in limites if item.status == "Solucao Viavel")
    total_clusters = sum(item.clusters for item in limites) or 1
    limite_total = sum((item.limite_sugerido or 0) * item.clusters for item in limites)
    taxa = clusters_viaveis / total_clusters * 100

    return ResultadosResponse(
        kpis=ResultadosKPIs(
            total_clusters=len(limites),
            limite_total_aprovado=_money(limite_total) or 0,
            clusters_ativos=clusters_viaveis,
            taxa_aprovacao=round(taxa, 2),
        ),
        limites_por_cluster=limites,
        distribuicao_status=[
            StatusDistribuicao(status="Ativo", quantidade=clusters_viaveis),
            StatusDistribuicao(status="Em Analise", quantidade=max(total_clusters - clusters_viaveis, 0)),
            StatusDistribuicao(status="Inativo", quantidade=0),
        ],
        evolucao_temporal_limites=[
            SeriePonto(label=f"M-{5 - index}", valor=round(limite_total * (0.72 + index * 0.07), 2))
            for index in range(6)
        ],
        distribuicao_score=[
            SeriePonto(label=label, valor=value)
            for label, value in [("300-499", 120), ("500-599", 360), ("600-699", 720), ("700-799", 1040), ("800-900", 610)]
        ],
    )


def export_resultados_csv() -> str:
    rows = [_dump_model(item) for item in get_resultados().limites_por_cluster]
    return pd.DataFrame(rows).to_csv(index=False)


def _sample_limites() -> list[LimiteCluster]:
    values = [1500, 5000, None, 200, 3600, 850, 12000]
    return [
        LimiteCluster(
            cluster_id=f"CLU-{index + 1:03d}",
            limite_sugerido=_money(value),
            status="Solucao Viavel" if value else "Sem Solucao",
            clusters=120 + index * 17,
        )
        for index, value in enumerate(values)
    ]


def _sample_clusters() -> list[Cluster]:
    limites = [5000, 9800, None, 18200, 8800, None, 15000, 4900]
    scores = [850, 720, 620, 910, 780, 450, 990, 680]
    statuses = ["Ativo", "Ativo", "Em Analise", "Ativo", "Ativo", "Inativo", "Ativo", "Ativo"]
    return [
        Cluster(
            id_=f"CLI-{index + 1:03d}",
            cluster=f"CLU-{(index % 5) + 1:03d}",
            score=scores[index],
            status=statuses[index],
            limite=_money(limites[index]),
            cadastro=_date_from_index(index),
        )
        for index in range(8)
    ]
