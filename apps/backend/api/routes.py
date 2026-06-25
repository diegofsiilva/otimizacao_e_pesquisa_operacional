"""
api/routes.py
Definição das rotas da API.
"""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    HTTPException,
    Query,
    Response,
    UploadFile,
)

from model.schemas import (
    ClienteHistoricoResponse,
    ClienteResultadoResponse,
    ClusterResultadoResponse,
    ConsultaCreate,
    ConsultaResponse,
    ParametrosModelo,
    PaginacaoParams,
    SafraResponse,
)
from services.credit_service import (
    calcular_z_banco,
    criar_consulta,
    exportar_clientes_csv,
    exportar_clientes_pulp_csv,
    get_clientes,
    get_clusters,
    get_config,
    get_consulta,
    get_consultas,
    get_historico_cliente,
    get_safras,
    update_config,
)

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """Health check da API.

    Não depende de banco nem de estado; serve para liveness/readiness probes.

    Returns:
        ``{"status": "ok"}`` com HTTP 200 sempre que a aplicação está no ar.
    """
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Safras
# ---------------------------------------------------------------------------


@router.get("/safras", response_model=list[SafraResponse])
async def listar_safras() -> list[SafraResponse]:
    """Lista as safras já carregadas no sistema.

    Returns:
        Lista de ``SafraResponse`` (número e metadados de cada safra), possivelmente
        vazia quando nenhuma base foi carregada ainda.
    """
    return await get_safras()


# ---------------------------------------------------------------------------
# Consultas
# ---------------------------------------------------------------------------


@router.get("/consultas", response_model=list[ConsultaResponse])
async def listar_consultas() -> list[ConsultaResponse]:
    """Lista todas as consultas (jobs de otimização) registradas.

    Returns:
        Lista de ``ConsultaResponse`` com status e metadados de cada consulta,
        usada pelo frontend para localizar a consulta concluída mais recente.
    """
    return await get_consultas()


@router.post("/consultas", response_model=ConsultaResponse, status_code=201)
async def upload_e_criar_consulta(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    safra_numero: int | None = Query(default=None, ge=1),
    usar_safra_existente: bool = Query(default=False),
    t: float | None = Query(default=None, gt=0),
    LGD: float | None = Query(default=None, gt=0, le=1),
    u_bar: float | None = Query(default=None, gt=0, le=1),
    L_max: float | None = Query(default=None, gt=0),
    T: float | None = Query(default=None, gt=0),
    taxa_conversao: float | None = Query(default=None, gt=0, le=1),
) -> ConsultaResponse:
    """
    Faz upload do parquet, resolve a safra e dispara o pipeline em background.

    Parâmetros de modelo são opcionais - se omitidos, os valores padrão
    de ParametrosModelo são utilizados.

    Retorna 409 se safra_numero informado já existir e usar_safra_existente
    for False, indicando ao front que deve exibir o popup de confirmação.
    """
    nome_arquivo = file.filename or "base.parquet"
    if Path(nome_arquivo).name != nome_arquivo:
        raise HTTPException(status_code=400, detail="Nome de arquivo invalido.")
    if not nome_arquivo.lower().endswith(".parquet"):
        raise HTTPException(
            status_code=400,
            detail="Formato invalido. Envie um arquivo .parquet.",
        )

    conteudo = await file.read()

    # monta overrides de parâmetros - apenas os que foram informados
    overrides = {
        k: v
        for k, v in {
            "t": t,
            "LGD": LGD,
            "u_bar": u_bar,
            "L_max": L_max,
            "T": T,
            "taxa_conversao": taxa_conversao,
        }.items()
        if v is not None
    }

    payload = ConsultaCreate(
        nome_arquivo_parquet=nome_arquivo,
        safra_numero=safra_numero,
        parametros=ParametrosModelo(**{**ParametrosModelo().model_dump(), **overrides}),
    )

    try:
        return await criar_consulta(
            payload,
            conteudo,
            background_tasks,
            usar_safra_existente=usar_safra_existente,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/consultas/{consulta_id}", response_model=ConsultaResponse)
async def detalhe_consulta(consulta_id: UUID) -> ConsultaResponse:
    """Retorna os detalhes e o status de uma consulta específica.

    Args:
        consulta_id: Identificador (UUID) da consulta.

    Returns:
        O ``ConsultaResponse`` correspondente.

    Raises:
        HTTPException: 404 quando a consulta não existe.
    """
    consulta = await get_consulta(consulta_id)
    if consulta is None:
        raise HTTPException(status_code=404, detail="Consulta não encontrada.")
    return consulta


@router.get(
    "/consultas/{consulta_id}/clusters", response_model=list[ClusterResultadoResponse]
)
async def listar_clusters(consulta_id: UUID) -> list[ClusterResultadoResponse]:
    """Lista os resultados agregados por cluster de uma consulta.

    Args:
        consulta_id: Identificador (UUID) da consulta.

    Returns:
        Lista de ``ClusterResultadoResponse`` com limite otimizado, PD e demais
        métricas por cluster.

    Raises:
        HTTPException: 404 quando a consulta não existe.
    """
    clusters = await get_clusters(consulta_id)
    if clusters is None:
        raise HTTPException(status_code=404, detail="Consulta não encontrada.")
    return clusters


@router.get(
    "/consultas/{consulta_id}/clientes", response_model=list[ClienteResultadoResponse]
)
async def listar_clientes(
    consulta_id: UUID,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> list[ClienteResultadoResponse]:
    """Lista os clientes de uma consulta, de forma paginada.

    Args:
        consulta_id: Identificador (UUID) da consulta.
        limit: Tamanho da página (1 a 1000; padrão 100).
        offset: Quantidade de registros a pular (>= 0; padrão 0).

    Returns:
        Lista de ``ClienteResultadoResponse`` com o resultado por cliente.

    Raises:
        HTTPException: 404 quando a consulta não existe.
    """
    clientes = await get_clientes(consulta_id, limit=limit, offset=offset)
    if clientes is None:
        raise HTTPException(status_code=404, detail="Consulta não encontrada.")
    return clientes


@router.get("/consultas/{consulta_id}/clientes/export")
async def exportar_clientes(consulta_id: UUID) -> Response:
    """Exporta os clientes de uma consulta como CSV para download.

    Usa os limites otimizados pelo Simplex próprio do projeto.

    Args:
        consulta_id: Identificador (UUID) da consulta.

    Returns:
        ``Response`` ``text/csv`` com cabeçalho ``Content-Disposition`` de
        attachment (``clientes_<id>.csv``).

    Raises:
        HTTPException: 404 quando a consulta não existe.
    """
    csv = await exportar_clientes_csv(consulta_id)
    if csv is None:
        raise HTTPException(status_code=404, detail="Consulta não encontrada.")
    return Response(
        content=csv,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="clientes_{consulta_id}.csv"'
        },
    )


@router.get("/consultas/{consulta_id}/clientes/export-pulp")
async def exportar_clientes_pulp(consulta_id: UUID) -> Response:
    """Exporta os clientes de uma consulta como CSV, na versão PuLP.

    Equivalente a :func:`exportar_clientes`, mas usando os limites calculados
    pelo solver de referência PuLP, para comparação.

    Args:
        consulta_id: Identificador (UUID) da consulta.

    Returns:
        ``Response`` ``text/csv`` como attachment (``clientes_pulp_<id>.csv``).

    Raises:
        HTTPException: 404 quando a consulta não existe.
    """
    csv = await exportar_clientes_pulp_csv(consulta_id)
    if csv is None:
        raise HTTPException(status_code=404, detail="Consulta não encontrada.")
    return Response(
        content=csv,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="clientes_pulp_{consulta_id}.csv"'
        },
    )


@router.get("/consultas/{consulta_id}/z-banco")
async def z_banco(consulta_id: UUID) -> dict:
    """Calcula o ``z`` da política atual do banco para a consulta (baseline).

    Serve de comparação contra o ``z`` otimizado: quanto o banco ganharia
    mantendo os limites vigentes versus os limites propostos pelo modelo.

    Args:
        consulta_id: Identificador (UUID) da consulta.

    Returns:
        ``dict`` com o valor de ``z`` do banco e métricas associadas.

    Raises:
        HTTPException: 404 quando a consulta não existe.
    """
    resultado = await calcular_z_banco(consulta_id)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Consulta não encontrada.")
    return resultado


# ---------------------------------------------------------------------------
# Clientes
# ---------------------------------------------------------------------------


@router.get("/clientes/{token}", response_model=ClienteHistoricoResponse)
async def historico_cliente(token: int) -> ClienteHistoricoResponse:
    """Retorna a evolução de um cliente ao longo das safras.

    Args:
        token: Token (identificador anonimizado) do cliente.

    Returns:
        ``ClienteHistoricoResponse`` com limite, PD, cluster e demais campos por
        safra em que o cliente aparece.

    Raises:
        HTTPException: 404 quando o cliente não é encontrado.
    """
    historico = await get_historico_cliente(token)
    if historico is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    return historico


# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------


@router.get("/config", response_model=ParametrosModelo)
async def get_parametros() -> ParametrosModelo:
    """Retorna os parâmetros de modelo atualmente configurados.

    Returns:
        ``ParametrosModelo`` com os valores vigentes (usados como padrão em novas
        consultas e exibidos no modal de configuração do frontend).
    """
    return await get_config()


@router.put("/config", response_model=ParametrosModelo)
async def atualizar_parametros(payload: ParametrosModelo) -> ParametrosModelo:
    """Atualiza e persiste os parâmetros de modelo.

    Args:
        payload: Novo conjunto de parâmetros (``ParametrosModelo``) a persistir.

    Returns:
        Os parâmetros efetivamente gravados.
    """
    return await update_config(payload)
