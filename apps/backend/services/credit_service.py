"""
services/credit_service.py
Lógica de negócio da API. Funções chamadas pelas rotas.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from config import UPLOAD_DIR
from db.storage import get_pool
from model.schemas import (
    ClienteHistoricoResponse,
    ClienteResultadoResponse,
    ClusterResultadoResponse,
    ConsultaCreate,
    ConsultaResponse,
    ParametrosModelo,
    SafraResponse,
)


def _agora() -> str:
    """Retorna o timestamp atual em UTC no formato ISO 8601."""
    return datetime.now(timezone.utc).isoformat()


def _row_para_parametros(row) -> ParametrosModelo:
    """Converte um registro da tabela config em ParametrosModelo."""
    return ParametrosModelo(
        t=row["t"],
        LGD=row["LGD"],
        u_bar=row["u_bar"],
        L_max=row["L_max"],
        T=row["T"],
    )


def _row_para_consulta(row) -> ConsultaResponse:
    """Converte um registro da tabela consultas em ConsultaResponse."""
    return ConsultaResponse(
        id=row["id"],
        safra_id=row["safra_id"],
        nome_arquivo_parquet=row["nome_arquivo_parquet"],
        parametros=ParametrosModelo.model_validate_json(row["parametros"]),
        status_consulta=row["status_consulta"],
        status_lp=row["status_lp"],
        z_otimo=row["z_otimo"],
        n_clientes_total=row["n_clientes_total"],
        n_clientes_elegiveis=row["n_clientes_elegiveis"],
        n_clientes_ofertados=row["n_clientes_ofertados"],
        n_clusters=row["n_clusters"],
        criado_em=datetime.fromisoformat(row["criado_em"]),
        iniciado_em=(
            datetime.fromisoformat(row["iniciado_em"]) if row["iniciado_em"] else None
        ),
        concluido_em=(
            datetime.fromisoformat(row["concluido_em"]) if row["concluido_em"] else None
        ),
        erro_etapa=row["erro_etapa"],
        erro_mensagem=row["erro_mensagem"],
    )


# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------


async def get_config() -> ParametrosModelo:
    """Retorna os parâmetros padrão do modelo lidos da tabela config."""
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT t, LGD, u_bar, L_max, T FROM config LIMIT 1")
    return _row_para_parametros(row)


async def update_config(payload: ParametrosModelo) -> ParametrosModelo:
    """Atualiza os parâmetros padrão do modelo na tabela config."""
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE config SET t = $1, LGD = $2, u_bar = $3, L_max = $4, T = $5",
            payload.t,
            payload.LGD,
            payload.u_bar,
            payload.L_max,
            payload.T,
        )
    return payload


# ---------------------------------------------------------------------------
# Safras
# ---------------------------------------------------------------------------


async def get_safras() -> list[SafraResponse]:
    """Retorna todas as safras ordenadas pelo número."""
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, numero, nome, criado_em FROM safras ORDER BY numero ASC"
        )
    return [
        SafraResponse(
            id=row["id"],
            numero=row["numero"],
            nome=row["nome"],
            criado_em=datetime.fromisoformat(row["criado_em"]),
        )
        for row in rows
    ]


async def _resolver_safra(conn, safra_numero: int | None, usar_existente: bool) -> str:
    """
    Resolve qual safra usar e retorna o safra_id.

    Regras:
        - safra_numero omitido: cria a próxima safra disponível (MAX + 1 ou M1)
        - safra_numero informado e não existe: cria com esse número
        - safra_numero informado e já existe com usar_existente=True: usa a existente
        - safra_numero informado e já existe com usar_existente=False: lança ValueError
    """
    if safra_numero is None:
        row = await conn.fetchrow("SELECT MAX(numero) AS max_num FROM safras")
        proximo = (row["max_num"] or 0) + 1
        return await _criar_safra(conn, proximo)

    row = await conn.fetchrow("SELECT id FROM safras WHERE numero = $1", safra_numero)

    if row is None:
        return await _criar_safra(conn, safra_numero)

    if usar_existente:
        return row["id"]

    raise ValueError(
        f"Safra M{safra_numero} já existe. "
        "Confirme se deseja usar a safra existente ou criar uma nova."
    )


async def _criar_safra(conn, numero: int) -> str:
    """Insere uma nova safra no banco e retorna o id gerado."""
    safra_id = str(uuid.uuid4())
    await conn.execute(
        "INSERT INTO safras (id, numero, nome, criado_em) VALUES ($1, $2, $3, $4)",
        safra_id,
        numero,
        f"M{numero}",
        _agora(),
    )
    return safra_id


# ---------------------------------------------------------------------------
# Consultas
# ---------------------------------------------------------------------------


async def get_consultas() -> list[ConsultaResponse]:
    """Retorna todas as consultas ordenadas da mais recente para a mais antiga."""
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM consultas ORDER BY criado_em DESC")
    return [_row_para_consulta(row) for row in rows]


async def get_consulta(consulta_id: UUID) -> ConsultaResponse | None:
    """Retorna uma consulta pelo id, ou None se não encontrada."""
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM consultas WHERE id = $1", str(consulta_id)
        )
    if row is None:
        return None
    return _row_para_consulta(row)


async def criar_consulta(
    payload: ConsultaCreate,
    conteudo: bytes,
    usar_safra_existente: bool = False,
) -> ConsultaResponse:
    """
    Salva o parquet, resolve a safra, insere a consulta no banco
    e dispara o pipeline em background.

    Lança ValueError se safra_numero já existir e usar_safra_existente for False.
    """
    # salva o parquet em disco
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    destino = UPLOAD_DIR / payload.nome_arquivo_parquet
    destino.write_bytes(conteudo)

    pool = get_pool()
    consulta_id = str(uuid.uuid4())

    async with pool.acquire() as conn:
        safra_id = await _resolver_safra(
            conn, payload.safra_numero, usar_safra_existente
        )

        await conn.execute(
            """
            INSERT INTO consultas (
                id, safra_id, nome_arquivo_parquet, parametros,
                status_consulta, criado_em
            ) VALUES ($1, $2, $3, $4, $5, $6)
            """,
            consulta_id,
            safra_id,
            payload.nome_arquivo_parquet,
            payload.parametros.model_dump_json(),
            "pendente",
            _agora(),
        )

    # TODO: disparar o pipeline em background
    # background_tasks.add_task(executar_pipeline, consulta_id, destino, payload.parametros)

    return await get_consulta(UUID(consulta_id))


# Clusters


async def get_clusters(consulta_id: UUID) -> list[ClusterResultadoResponse] | None:
    """
    Retorna os clusters de uma consulta ordenados pelo cluster_id.
    Retorna None se a consulta não existir.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        existe = await conn.fetchval(
            "SELECT 1 FROM consultas WHERE id = $1", str(consulta_id)
        )
        if not existe:
            return None

        rows = await conn.fetch(
            """
            SELECT cluster_id, n_clientes, pd_media, pi_media, cp_percentil5,
                   score_credito_cross_medio, ck_medio, fator_alavancagem, limite_otimizado
            FROM clusters_resultado
            WHERE consulta_id = $1
            ORDER BY cluster_id ASC
            """,
            str(consulta_id),
        )

    return [
        ClusterResultadoResponse(
            cluster_id=row["cluster_id"],
            n_clientes=row["n_clientes"],
            pd_media=row["pd_media"],
            pi_media=row["pi_media"],
            cp_percentil5=row["cp_percentil5"],
            score_credito_cross_medio=row["score_credito_cross_medio"],
            ck_medio=row["ck_medio"],
            fator_alavancagem=row["fator_alavancagem"],
            limite_otimizado=row["limite_otimizado"],
        )
        for row in rows
    ]


# Clientes


async def get_clientes(
    consulta_id: UUID,
    limit: int = 100,
    offset: int = 0,
) -> list[ClienteResultadoResponse] | None:
    """
    Retorna os clientes de uma consulta com paginação.
    Retorna None se a consulta não existir.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        existe = await conn.fetchval(
            "SELECT 1 FROM consultas WHERE id = $1", str(consulta_id)
        )
        if not existe:
            return None

        rows = await conn.fetch(
            """
            SELECT *
            FROM clientes_resultado
            WHERE consulta_id = $1
            ORDER BY token ASC
            LIMIT $2 OFFSET $3
            """,
            str(consulta_id),
            limit,
            offset,
        )

    return [_row_para_cliente(row) for row in rows]


async def exportar_clientes_csv(consulta_id: UUID) -> str | None:
    """
    Retorna todos os clientes de uma consulta como CSV.
    Retorna None se a consulta não existir.
    """
    import io
    import pandas as pd

    pool = get_pool()
    async with pool.acquire() as conn:
        existe = await conn.fetchval(
            "SELECT 1 FROM consultas WHERE id = $1", str(consulta_id)
        )
        if not existe:
            return None

        rows = await conn.fetch(
            "SELECT * FROM clientes_resultado WHERE consulta_id = $1 ORDER BY token ASC",
            str(consulta_id),
        )

    df = pd.DataFrame([dict(row) for row in rows])
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue()


async def get_historico_cliente(token: int) -> ClienteHistoricoResponse | None:
    """
    Retorna o histórico de um cliente em todas as consultas em que apareceu.
    Retorna None se o token não existir em nenhuma consulta.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT *
            FROM clientes_resultado
            WHERE token = $1
            ORDER BY consulta_id ASC
            """,
            token,
        )

    if not rows:
        return None

    return ClienteHistoricoResponse(
        token=token,
        historico=[_row_para_cliente(row) for row in rows],
    )


def _row_para_cliente(row) -> ClienteResultadoResponse:
    """Converte um registro da tabela clientes_resultado em ClienteResultadoResponse."""
    return ClienteResultadoResponse(
        token=row["token"],
        consulta_id=row["consulta_id"],
        safra_ref_uso=row["safra_ref_uso"],
        score_interno=row["score_interno"],
        pd_produto=row["pd_produto"],
        score_generico_1=row["score_generico_1"],
        score_generico_2=row["score_generico_2"],
        capacidade_pagamento=row["capacidade_pagamento"],
        delta_capacidade_pagamento=row["delta_capacidade_pagamento"],
        score_propensao_contrato=row["score_propensao_contrato"],
        score_credito_cross=row["score_credito_cross"],
        renda_estimada=row["renda_estimada"],
        fx_idade=row["fx_idade"],
        limite_ofertado=row["limite_ofertado"],
        flag_contrato=row["flag_contrato"],
        flag_ativacao=row["flag_ativacao"],
        over30mob3=row["over30mob3"],
        pd_calibrada=row["pd_calibrada"],
        pi_normalizado=row["pi_normalizado"],
        cp_proxy=row["cp_proxy"],
        cluster_id=row["cluster_id"],
        limite_otimizado=row["limite_otimizado"],
    )


# ---------------------------------------------------------------------------
# Clusters
# ---------------------------------------------------------------------------


async def get_clusters(consulta_id: UUID) -> list[ClusterResultadoResponse] | None:
    """
    Retorna os clusters de uma consulta ordenados por cluster_id.
    Retorna None se a consulta não existir.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        existe = await conn.fetchval(
            "SELECT 1 FROM consultas WHERE id = $1", str(consulta_id)
        )
        if not existe:
            return None

        rows = await conn.fetch(
            """
            SELECT cluster_id, n_clientes, pd_media, pi_media, cp_percentil5,
                   score_credito_cross_medio, ck_medio, fator_alavancagem, limite_otimizado
            FROM clusters_resultado
            WHERE consulta_id = $1
            ORDER BY cluster_id ASC
            """,
            str(consulta_id),
        )

    return [
        ClusterResultadoResponse(
            cluster_id=row["cluster_id"],
            n_clientes=row["n_clientes"],
            pd_media=row["pd_media"],
            pi_media=row["pi_media"],
            cp_percentil5=row["cp_percentil5"],
            score_credito_cross_medio=row["score_credito_cross_medio"],
            ck_medio=row["ck_medio"],
            fator_alavancagem=row["fator_alavancagem"],
            limite_otimizado=row["limite_otimizado"],
        )
        for row in rows
    ]


# ---------------------------------------------------------------------------
# Clientes
# ---------------------------------------------------------------------------


async def get_clientes(
    consulta_id: UUID,
    limit: int = 100,
    offset: int = 0,
) -> list[ClienteResultadoResponse] | None:
    """
    Retorna os clientes de uma consulta com paginação.
    Retorna None se a consulta não existir.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        existe = await conn.fetchval(
            "SELECT 1 FROM consultas WHERE id = $1", str(consulta_id)
        )
        if not existe:
            return None

        rows = await conn.fetch(
            """
            SELECT *
            FROM clientes_resultado
            WHERE consulta_id = $1
            ORDER BY token ASC
            LIMIT $2 OFFSET $3
            """,
            str(consulta_id),
            limit,
            offset,
        )

    return [_row_para_cliente(row) for row in rows]


async def exportar_clientes_csv(consulta_id: UUID) -> str | None:
    """
    Retorna todos os clientes de uma consulta serializados como CSV.
    Retorna None se a consulta não existir.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        existe = await conn.fetchval(
            "SELECT 1 FROM consultas WHERE id = $1", str(consulta_id)
        )
        if not existe:
            return None

        rows = await conn.fetch(
            "SELECT * FROM clientes_resultado WHERE consulta_id = $1 ORDER BY token ASC",
            str(consulta_id),
        )

    import io
    import csv

    buffer = io.StringIO()
    if rows:
        writer = csv.DictWriter(buffer, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows([dict(row) for row in rows])

    return buffer.getvalue()


async def get_historico_cliente(token: int) -> ClienteHistoricoResponse | None:
    """
    Retorna o histórico completo de um cliente em todas as consultas.
    Retorna None se o token não existir em nenhuma consulta.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT *
            FROM clientes_resultado
            WHERE token = $1
            ORDER BY consulta_id ASC
            """,
            token,
        )

    if not rows:
        return None

    return ClienteHistoricoResponse(
        token=token,
        historico=[_row_para_cliente(row) for row in rows],
    )


def _row_para_cliente(row) -> ClienteResultadoResponse:
    """Converte um registro da tabela clientes_resultado em ClienteResultadoResponse."""
    return ClienteResultadoResponse(
        token=row["token"],
        consulta_id=row["consulta_id"],
        safra_ref_uso=row["safra_ref_uso"],
        score_interno=row["score_interno"],
        pd_produto=row["pd_produto"],
        score_generico_1=row["score_generico_1"],
        score_generico_2=row["score_generico_2"],
        capacidade_pagamento=row["capacidade_pagamento"],
        delta_capacidade_pagamento=row["delta_capacidade_pagamento"],
        score_propensao_contrato=row["score_propensao_contrato"],
        score_credito_cross=row["score_credito_cross"],
        renda_estimada=row["renda_estimada"],
        fx_idade=row["fx_idade"],
        limite_ofertado=row["limite_ofertado"],
        flag_contrato=row["flag_contrato"],
        flag_ativacao=row["flag_ativacao"],
        over30mob3=row["over30mob3"],
        pd_calibrada=row["pd_calibrada"],
        pi_normalizado=row["pi_normalizado"],
        cp_proxy=row["cp_proxy"],
        cluster_id=row["cluster_id"],
        limite_otimizado=row["limite_otimizado"],
    )

# TODO: que falta é a função executar_pipeline que roda em background. É a mais complexa porque integra o pipeline do otimizador com o banco de dados.
