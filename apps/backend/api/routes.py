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
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Safras
# ---------------------------------------------------------------------------


@router.get("/safras", response_model=list[SafraResponse])
async def listar_safras() -> list[SafraResponse]:
    return await get_safras()


# ---------------------------------------------------------------------------
# Consultas
# ---------------------------------------------------------------------------


@router.get("/consultas", response_model=list[ConsultaResponse])
async def listar_consultas() -> list[ConsultaResponse]:
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
    consulta = await get_consulta(consulta_id)
    if consulta is None:
        raise HTTPException(status_code=404, detail="Consulta não encontrada.")
    return consulta


@router.get(
    "/consultas/{consulta_id}/clusters", response_model=list[ClusterResultadoResponse]
)
async def listar_clusters(consulta_id: UUID) -> list[ClusterResultadoResponse]:
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
    clientes = await get_clientes(consulta_id, limit=limit, offset=offset)
    if clientes is None:
        raise HTTPException(status_code=404, detail="Consulta não encontrada.")
    return clientes


@router.get("/consultas/{consulta_id}/clientes/export")
async def exportar_clientes(consulta_id: UUID) -> Response:
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
    resultado = await calcular_z_banco(consulta_id)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Consulta não encontrada.")
    return resultado


# ---------------------------------------------------------------------------
# Clientes
# ---------------------------------------------------------------------------


@router.get("/clientes/{token}", response_model=ClienteHistoricoResponse)
async def historico_cliente(token: int) -> ClienteHistoricoResponse:
    historico = await get_historico_cliente(token)
    if historico is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    return historico


# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------


@router.get("/config", response_model=ParametrosModelo)
async def get_parametros() -> ParametrosModelo:
    return await get_config()


@router.put("/config", response_model=ParametrosModelo)
async def atualizar_parametros(payload: ParametrosModelo) -> ParametrosModelo:
    return await update_config(payload)
