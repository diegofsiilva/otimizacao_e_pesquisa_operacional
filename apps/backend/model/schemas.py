"""
model/schemas.py
Schemas Pydantic para entrada e saída dos endpoints da API.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

StatusConsulta = Literal["pendente", "executando", "concluido", "erro"]
StatusLP = Literal["otimo", "multiplas_solucoes"]
StatusLPPulp = Literal["otimo", "ilimitado", "inviavel", "erro"]
ErroEtapa = Literal["calibracao", "clustering", "otimizacao"]


class SafraCreate(BaseModel):
    """
    Payload para criação de uma safra.

    Atributos:
        numero : número da safra (ex: 1 para M1). Se omitido, o backend
                 atribui o próximo número disponível automaticamente.
    """

    numero: int | None = Field(default=None, ge=1)


class SafraResponse(BaseModel):
    """Representação de uma safra retornada pela API."""

    id: UUID
    numero: int
    nome: str
    criado_em: datetime


class ParametrosModelo(BaseModel):
    """
    Parâmetros do modelo de otimização de limites de crédito.
    Todos os campos possuem valores padrão e podem ser omitidos.
    """

    # taxa de interchange recebida pelo banco sobre o volume transacionado
    t: float = Field(default=0.0175, gt=0)

    # fração da exposição perdida em caso de default
    LGD: float = Field(default=0.8, gt=0, le=1)

    # fração esperada de utilização do limite pelo cliente
    u_bar: float = Field(default=0.75, gt=0, le=1)

    # teto máximo absoluto de limite por cluster em reais
    L_max: float = Field(default=25000.0, gt=0)

    # horizonte de uso do limite em meses
    T: float = Field(default=22.0, gt=0)


class ConsultaCreate(BaseModel):
    """
    Payload para criação de uma consulta.

    Atributos:
        nome_arquivo_parquet : nome do arquivo parquet a ser processado
        safra_numero         : número da safra. Se omitido, o backend aplica
                               a lógica de auto-incremento
        parametros           : parâmetros do modelo. Se omitidos, os valores
                               padrão de ParametrosModelo são utilizados
    """

    nome_arquivo_parquet: str
    safra_numero: int | None = Field(default=None, ge=1)
    parametros: ParametrosModelo = Field(default_factory=ParametrosModelo)


class ConsultaResponse(BaseModel):
    """
    Representação de uma consulta retornada pela API.
    Campos de resultado (z_otimo, contagens) são null até a conclusão.
    """

    id: UUID
    safra_id: UUID
    nome_arquivo_parquet: str
    parametros: ParametrosModelo
    status_consulta: StatusConsulta
    status_lp: StatusLP | None = None
    z_otimo: float | None = None
    z_pulp: float | None = None
    status_lp_pulp: StatusLPPulp | None = None
    delta_z_pct: float | None = None
    n_clientes_total: int | None = None
    n_clientes_elegiveis: int | None = None
    n_clientes_ofertados: int | None = None
    n_clusters: int | None = None
    criado_em: datetime
    iniciado_em: datetime | None = None
    concluido_em: datetime | None = None
    erro_etapa: ErroEtapa | None = None
    erro_mensagem: str | None = None


class ClusterResultadoResponse(BaseModel):
    """Representação de um cluster com seus parâmetros agregados e limite otimizado."""

    segmento_id: int
    n_clientes: int
    pd_media: float
    pi_media: float
    cp_percentil5: float
    score_credito_cross_medio: float
    ck_medio: float
    fator_alavancagem: float
    limite_otimizado: int
    limite_otimizado_pulp: int | None = None


class PaginacaoParams(BaseModel):
    """
    Parâmetros de paginação reutilizados nos endpoints que retornam listas longas.

    Atributos:
        limit  : número máximo de registros por página
        offset : deslocamento a partir do primeiro registro
    """

    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class ClienteResultadoResponse(BaseModel):
    """
    Representação de um cliente elegível com todos os dados disponíveis,
    incluindo os campos originais do parquet, os campos derivados pelo
    pipeline e a atribuição de cluster e limite.
    """

    # identificação
    token: int
    consulta_id: UUID
    safra_ref_uso: str

    # campos originais do parquet
    score_interno: int
    pd_produto: float
    score_generico_1: int | None = None
    score_generico_2: int | None = None
    capacidade_pagamento: float | None = None
    delta_capacidade_pagamento: float | None = None
    score_propensao_contrato: float
    score_credito_cross: int
    renda_estimada: float | None = None
    fx_idade: str
    limite_ofertado: float | None = None
    flag_contrato: int
    flag_ativacao: int
    over30mob3: int | None = None

    # campos derivados pelo pipeline
    pd_calibrada: float
    pi_normalizado: float
    cp_proxy: float

    # atribuição pelo clustering e LP
    segmento_id: int
    limite_otimizado: int


class ClienteHistoricoResponse(BaseModel):
    """
    Histórico de um cliente específico ao longo das consultas.
    Retorna uma lista de registros, um por consulta em que o token apareceu.
    """

    token: int
    historico: list[ClienteResultadoResponse]
