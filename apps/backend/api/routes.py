from fastapi import APIRouter, File, HTTPException, Query, Response, UploadFile

from model.schemas import Cluster, DashboardResponse, GeracaoLimitesResponse, ParametrosModelo, ResultadosResponse
from services.credit_service import (
    delete_cliente,
    export_resultados_csv,
    gerar_limites,
    get_dashboard,
    get_parametros,
    get_resultados,
    list_clientes,
    save_upload,
    update_parametros,
    upsert_cliente,
)


router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/supabase/health")
def supabase_health() -> dict[str, str]:
    import os

    configured = bool(os.getenv("SUPABASE_URL")) and bool(
        os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    )
    # Se estiver configurado, forca uma leitura leve (vai falhar se a tabela nao existir).
    if configured:
        from db.storage import load_state

        _ = load_state()
    return {"configured": str(configured).lower(), "status": "ok"}


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard() -> DashboardResponse:
    return get_dashboard()


@router.get("/clientes", response_model=list[Cluster])
def clientes(q: str | None = None, status: str | None = None) -> list[Cluster]:
    return list_clientes(q=q, status=status)


@router.post("/clientes", response_model=Cluster, status_code=201)
def criar_cliente(payload: Cluster) -> Cluster:
    return upsert_cliente(payload)


@router.delete("/clientes/{cliente_id}", status_code=204)
def remover_cliente(cliente_id: str) -> Response:
    deleted = delete_cliente(cliente_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Cluster nao encontrado.")
    return Response(status_code=204)


@router.get("/config", response_model=ParametrosModelo)
def parametros() -> ParametrosModelo:
    return get_parametros()


@router.put("/config", response_model=ParametrosModelo)
def atualizar_parametros(payload: ParametrosModelo) -> ParametrosModelo:
    return update_parametros(payload)


@router.post("/limites/gerar", response_model=GeracaoLimitesResponse)
async def upload_e_gerar_limites(
    file: UploadFile = File(...),
    n_clusters: int | None = Query(default=None, ge=1, le=30),
) -> GeracaoLimitesResponse:
    try:
        path = save_upload(file.filename or "base.csv", await file.read())
        return gerar_limites(path, n_clusters=n_clusters)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/resultados", response_model=ResultadosResponse)
def resultados() -> ResultadosResponse:
    return get_resultados()


@router.get("/resultados/export")
def exportar_resultados() -> Response:
    csv = export_resultados_csv()
    return Response(
        content=csv,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="resultados_limites.csv"'},
    )
