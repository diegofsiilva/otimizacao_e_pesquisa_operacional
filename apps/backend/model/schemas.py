from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


ClusterStatus = Literal["Ativo", "Em Analise", "Inativo"]
SolutionStatus = Literal["Solucao Viavel", "Sem Solucao"]


class Cluster(BaseModel):
    id_: str
    cluster: str | None = None
    score: float | None = None
    status: ClusterStatus = "Ativo"
    limite: float | None = None
    cadastro: date | None = None


class DashboardKPIs(BaseModel):
    total_clientes: int
    clientes_ativos: int
    limite_total: float
    taxa_aprovacao: float


class DashboardResponse(BaseModel):
    kpis: DashboardKPIs
    clusters: list[Cluster]


class ParametrosModelo(BaseModel):
    t: float = Field(0.0175, ge=0)
    LGD: float = Field(0.8, ge=0, le=1)
    u_bar: float = Field(0.75, ge=0, le=1)
    L_max: float = Field(25000.0, ge=0)
    alpha: float = Field(0.05, ge=0, le=1)
    n_clusters: int = Field(7, ge=1, le=30)


class LimiteCluster(BaseModel):
    cluster_id: str
    limite_sugerido: float | None
    status: SolutionStatus
    clientes: int = 0


class GeracaoResumo(BaseModel):
    total_clusters: int
    com_solucao_viavel: int
    sem_solucao: int


class GeracaoLimitesResponse(BaseModel):
    arquivo: str
    resumo: GeracaoResumo
    limites: list[LimiteCluster]


class ResultadosKPIs(BaseModel):
    total_clusters: int
    limite_total_aprovado: float
    clientes_ativos: int
    taxa_aprovacao: float


class StatusDistribuicao(BaseModel):
    status: str
    quantidade: int


class SeriePonto(BaseModel):
    label: str
    valor: float


class ResultadosResponse(BaseModel):
    kpis: ResultadosKPIs
    limites_por_cluster: list[LimiteCluster]
    distribuicao_status: list[StatusDistribuicao]
    evolucao_temporal_limites: list[SeriePonto]
    distribuicao_score: list[SeriePonto]