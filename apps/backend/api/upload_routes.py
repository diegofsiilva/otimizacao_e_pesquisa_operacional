"""
api/upload_routes.py
Rotas para upload de arquivos grandes em chunks.

Endpoints:
    POST /api/uploads/iniciar
    POST /api/uploads/{upload_id}/chunk?index={n}
    POST /api/uploads/{upload_id}/finalizar
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, Query, UploadFile

from model.schemas import ConsultaCreate, ConsultaResponse, ParametrosModelo
from services.credit_service import criar_consulta_de_path
from services.upload_service import finalizar_upload, iniciar_upload, salvar_chunk

router = APIRouter()


@router.post("/uploads/iniciar")
async def rota_iniciar_upload(
    nome_arquivo: str = Query(
        ..., description="Nome do arquivo .parquet a ser enviado"
    ),
) -> dict:
    """
    Cria uma sessão de upload e retorna o upload_id.
    O cliente deve usar este ID em todas as chamadas subsequentes.
    """
    try:
        return iniciar_upload(nome_arquivo)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/uploads/{upload_id}/chunk")
async def rota_enviar_chunk(
    upload_id: str,
    index: int = Query(
        ..., ge=0, description="Índice sequencial do chunk, começando em 0"
    ),
    file: UploadFile = File(...),
) -> dict:
    """
    Recebe um chunk e o salva no diretório temporário do upload.
    Deve ser chamado sequencialmente para cada parte do arquivo.
    """
    dados = await file.read()
    try:
        salvar_chunk(upload_id, index, dados)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"ok": True, "index": index, "bytes": len(dados)}


@router.post(
    "/uploads/{upload_id}/finalizar",
    response_model=ConsultaResponse,
    status_code=201,
)
async def rota_finalizar_upload(
    upload_id: str,
    background_tasks: BackgroundTasks,
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
    Remonta o arquivo a partir dos chunks recebidos e dispara o pipeline.
    Retorna a ConsultaResponse com status 'pendente'.
    Retorna 409 se safra_numero já existir e usar_safra_existente for False.
    """
    try:
        parquet_path = finalizar_upload(upload_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

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
        nome_arquivo_parquet=parquet_path.name,
        safra_numero=safra_numero,
        parametros=ParametrosModelo(**{**ParametrosModelo().model_dump(), **overrides}),
    )

    try:
        return await criar_consulta_de_path(
            payload, parquet_path, background_tasks, usar_safra_existente
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
