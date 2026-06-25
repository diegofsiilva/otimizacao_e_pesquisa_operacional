"""
services/credit_service.py
Lógica de negócio da API. Funções chamadas pelas rotas.
"""

from __future__ import annotations

import csv
import io
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import pandas as pd
from fastapi import BackgroundTasks

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
    StatusLPPulp,
)


# Diretório onde cada consulta grava seu snapshot de clientes (parquet). Usa a
# MESMA raiz data/ que o otimizador usa para data/cache (parents[3] a partir de
# services/credit_service.py chega na raiz do repo). É persistente, NÃO é cache:
# é a fonte de verdade do detalhe por cliente, substituindo a antiga tabela
# clientes_resultado (que custava minutos de COPY a cada execução).
_RESULTADOS_DIR = Path(__file__).resolve().parents[3] / "data" / "resultados"


def _agora() -> str:
    """Retorna o timestamp atual em UTC no formato ISO 8601."""
    return datetime.now(timezone.utc).isoformat()


def _row_para_parametros(row) -> ParametrosModelo:
    """Converte um registro da tabela parametros_modelo em ParametrosModelo."""
    return ParametrosModelo(
        t=row["t"],
        LGD=row["LGD"],
        u_bar=row["u_bar"],
        L_max=row["L_max"],
        T=row["T"],
        comparar_pulp=row["comparar_pulp"],
        taxa_conversao=row["taxa_conversao"],
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
        z_pulp=row["z_pulp"],
        status_lp_pulp=row["status_lp_pulp"],
        delta_z_pct=row["delta_z_pct"],
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
        segmento_id=row["segmento_id"],
        limite_otimizado=row["limite_otimizado"],
    )


def _cliente_de_serie(consulta_id, s) -> ClienteResultadoResponse:
    """Constrói um ClienteResultadoResponse a partir de uma linha (Series) do
    parquet de resultado. Mapeia a coluna 'pi' do parquet para pi_normalizado e
    converte NaN -> None nas colunas anuláveis."""

    def _i(v):
        return None if pd.isna(v) else int(v)

    def _f(v):
        return None if pd.isna(v) else float(v)

    return ClienteResultadoResponse(
        token=int(s["token"]),
        consulta_id=consulta_id,
        safra_ref_uso=str(s["safra_ref_uso"]),
        score_interno=int(s["score_interno"]),
        pd_produto=float(s["pd_produto"]),
        score_generico_1=_i(s["score_generico_1"]),
        score_generico_2=_i(s["score_generico_2"]),
        capacidade_pagamento=_f(s["capacidade_pagamento"]),
        delta_capacidade_pagamento=_f(s["delta_capacidade_pagamento"]),
        score_propensao_contrato=float(s["score_propensao_contrato"]),
        score_credito_cross=int(s["score_credito_cross"]),
        renda_estimada=_f(s["renda_estimada"]),
        fx_idade=str(s["fx_idade"]),
        limite_ofertado=_f(s["limite_ofertado"]),
        flag_contrato=int(s["flag_contrato"]),
        flag_ativacao=int(s["flag_ativacao"]),
        over30mob3=_i(s["over30mob3"]),
        pd_calibrada=float(s["pd_calibrada"]),
        pi_normalizado=float(s["pi"]),
        cp_proxy=float(s["cp_proxy"]),
        segmento_id=int(s["segmento_id"]),
        limite_otimizado=int(s["limite_otimizado"]),
    )


async def _carregar_clientes_consulta(consulta_id):
    """Carrega o snapshot de clientes de uma consulta como DataFrame.

    Fonte primária: data/resultados/<consulta_id>.parquet (gravado pelo
    pipeline). Fallback: a tabela clientes_resultado (consultas antigas,
    anteriores à migração para parquet). As colunas seguem a convenção do
    parquet (coluna 'pi'); o fallback renomeia pi_normalizado -> pi. Retorna
    None se não houver dados em lugar nenhum."""
    p = _RESULTADOS_DIR / f"{consulta_id}.parquet"
    if p.exists():
        return pd.read_parquet(p)

    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM clientes_resultado WHERE consulta_id = $1 "
            "ORDER BY token ASC",
            str(consulta_id),
        )
    if not rows:
        return None
    df = pd.DataFrame([dict(r) for r in rows])
    if "pi" not in df.columns and "pi_normalizado" in df.columns:
        df = df.rename(columns={"pi_normalizado": "pi"})
    return df


_COLS_CSV = [
    "consulta_id", "token", "safra_ref_uso", "score_interno", "pd_produto",
    "score_generico_1", "score_generico_2", "capacidade_pagamento",
    "delta_capacidade_pagamento", "score_propensao_contrato",
    "score_credito_cross", "renda_estimada", "fx_idade", "limite_ofertado",
    "flag_contrato", "flag_ativacao", "over30mob3", "pd_calibrada",
    "pi_normalizado", "cp_proxy", "segmento_id", "limite_otimizado",
]


def _clientes_para_csv(consulta_id, df, incluir_pulp=False) -> str:
    """Serializa o DataFrame de clientes como CSV, na mesma ordem de colunas que
    a tela espera. Renomeia 'pi' -> pi_normalizado e injeta consulta_id."""
    out = df.rename(columns={"pi": "pi_normalizado"}).copy()
    out["consulta_id"] = str(consulta_id)
    cols = list(_COLS_CSV)
    if incluir_pulp:
        cols = cols + ["limite_otimizado_pulp"]
    cols = [c for c in cols if c in out.columns]
    return out[cols].to_csv(index=False)


# ---------------------------------------------------------------------------
# Pipeline em background
# ---------------------------------------------------------------------------

# importa executar_pipeline pelo path absoluto para evitar conflito de nomes
# com o main.py do próprio backend
import importlib.util as _importlib_util

_OTIMIZADOR_MAIN = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "apps"
    / "algoritmo_simplex"
    / "main.py"
)
_OTIMIZADOR_DIR = str(_OTIMIZADOR_MAIN.parent)
if _OTIMIZADOR_DIR not in sys.path:
    sys.path.append(_OTIMIZADOR_DIR)

_spec = _importlib_util.spec_from_file_location(
    "algoritmo_simplex_main", _OTIMIZADOR_MAIN
)
_mod = _importlib_util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
_executar_pipeline = _mod.executar_pipeline


async def _pipeline_background(
    consulta_id: str, parquet_path: Path, params: dict
) -> None:
    """
    Executa o pipeline de otimização em background e persiste os resultados no banco.

    Fluxo:
        1. Marca a consulta como "executando"
        2. Chama executar_pipeline do otimizador (bloqueante -- roda em thread pool)
        3. Persiste clusters_resultado (insert normal -- 800 linhas)
        4. Persiste clientes_resultado (bulk insert -- até 3M linhas)
        5. Marca a consulta como "concluida" com todos os campos de resultado
        6. Em caso de erro, marca como "erro" com etapa e mensagem
    """
    import asyncio
    import pyarrow.parquet as pq

    pool = get_pool()

    # 1. marca como executando
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE consultas SET status_consulta = $1, iniciado_em = $2 WHERE id = $3",
            "executando",
            _agora(),
            consulta_id,
        )

    try:
        # lê o total de linhas do parquet raw sem carregar os dados em memória
        n_total = pq.read_metadata(parquet_path).num_rows

        # o toggle de comparação com PuLP é uma configuração GLOBAL (tela de
        # configurações), não um parâmetro por consulta. Lê do banco e injeta
        # no dict de parâmetros que o otimizador recebe.
        try:
            cfg = await get_config()
            params = {**params, "comparar_pulp": bool(cfg.comparar_pulp)}
        except Exception:
            params = {**params, "comparar_pulp": False}

        # 2. executa o pipeline numa thread para não bloquear a event loop
        loop = asyncio.get_running_loop()
        resultado = await loop.run_in_executor(
            None, _executar_pipeline, parquet_path, params
        )

        clusters = resultado["clusters"]
        z = resultado["z"]
        status_lp = resultado["status"]
        parquet_cc = resultado["parquet_com_cluster"]

        # 3. persiste clusters_resultado
        async with pool.acquire() as conn:
            await conn.executemany(
                """
                INSERT INTO clusters_resultado (
                    consulta_id, segmento_id, n_clientes, pd_media, pi_media,
                    cp_percentil5, score_credito_cross_medio, ck_medio,
                    fator_alavancagem, limite_otimizado, limite_otimizado_pulp
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """,
                [
                    (
                        consulta_id,
                        c["segmento_id"],
                        c["n_clientes"],
                        c["pd_media"],
                        c["pi_media"],
                        c["cp_percentil5"],
                        c["score_credito_cross_medio"],
                        c["ck_medio"],
                        c["fator_alavancagem"],
                        c["limite_otimizado"],
                        c["limite_otimizado_pulp"],
                    )
                    for c in clusters
                ],
            )

        # 4. persiste o resultado por cliente como snapshot parquet por consulta
        #    (antes era um COPY de ~1.8M linhas em clientes_resultado, ~5 min)
        df_cc = pd.read_parquet(parquet_cc)

        # mapa de limite por segmento_id para desnormalizar em clientes_resultado
        limite_por_cluster = {c["segmento_id"]: c["limite_otimizado"] for c in clusters}
        df_cc["limite_otimizado"] = (
            df_cc["segmento_id"].map(limite_por_cluster).fillna(0).astype(int)
        )

        # Persistência por consulta como PARQUET (substitui o COPY de ~1.8M
        # linhas no Postgres, que levava minutos). O que é único por consulta e
        # importa de verdade — o limite por segmento — já vai para
        # clusters_resultado (800 linhas). Aqui gravamos um snapshot por consulta
        # em data/resultados/<consulta_id>.parquet: escrita em frações de
        # segundo, histórico preservado e EXATO (captura pi/pd/limite no momento
        # do run). As telas de cliente leem esse arquivo sob demanda — ver
        # _carregar_clientes_consulta.
        mp_pulp = {
            c["segmento_id"]: c["limite_otimizado_pulp"] for c in clusters
        }
        df_cc["limite_otimizado_pulp"] = df_cc["segmento_id"].map(mp_pulp)
        # ordena por token p/ as telas paginarem sem reordenar a cada request
        df_cc = df_cc.sort_values("token")

        _RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)
        df_cc.to_parquet(
            _RESULTADOS_DIR / f"{consulta_id}.parquet", index=False
        )

        # 5. atualiza a consulta como concluída
        n_elegiveis = len(df_cc)
        n_ofertados = int((df_cc["limite_otimizado"] > 0).sum())

        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE consultas SET
                    status_consulta      = $1,
                    status_lp            = $2,
                    z_otimo              = $3,
                    z_pulp               = $4,
                    status_lp_pulp       = $5,
                    delta_z_pct          = $6,
                    n_clientes_total     = $7,
                    n_clientes_elegiveis = $8,
                    n_clientes_ofertados = $9,
                    n_clusters           = $10,
                    concluido_em         = $11
                WHERE id = $12
                """,
                "concluido",
                status_lp,
                z,
                resultado["z_pulp"],
                resultado["status_pulp"],
                resultado["delta_z_pct"],
                n_total,
                n_elegiveis,
                n_ofertados,
                len(clusters),
                _agora(),
                consulta_id,
            )

    except FileNotFoundError as exc:
        # erro recuperável do pipeline -- etapa identificada pelo prefixo da mensagem
        etapa = (
            "calibracao"
            if "[calibracao]" in str(exc)
            else "clustering" if "[clustering]" in str(exc) else "otimizacao"
        )
        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE consultas SET
                    status_consulta = $1, erro_etapa = $2,
                    erro_mensagem = $3, concluido_em = $4
                WHERE id = $5
                """,
                "erro",
                etapa,
                str(exc),
                _agora(),
                consulta_id,
            )
    except Exception as exc:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE consultas SET
                    status_consulta = $1, erro_etapa = $2,
                    erro_mensagem = $3, concluido_em = $4
                WHERE id = $5
                """,
                "erro",
                "otimizacao",
                str(exc),
                _agora(),
                consulta_id,
            )


# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------


async def get_config() -> ParametrosModelo:
    """Retorna os parâmetros padrão do modelo lidos da tabela parametros_modelo."""
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            'SELECT "t", "LGD", "u_bar", "L_max", "T", "comparar_pulp", "taxa_conversao" '
            "FROM parametros_modelo LIMIT 1"
        )
    if row is None:
        return ParametrosModelo()
    return _row_para_parametros(row)


async def update_config(payload: ParametrosModelo) -> ParametrosModelo:
    """Atualiza os parâmetros padrão do modelo na tabela parametros_modelo."""
    pool = get_pool()
    async with pool.acquire() as conn:
        status = await conn.execute(
            'UPDATE parametros_modelo SET "t" = $1, "LGD" = $2, "u_bar" = $3, '
            '"L_max" = $4, "T" = $5, "comparar_pulp" = $6, "taxa_conversao" = $7',
            payload.t,
            payload.LGD,
            payload.u_bar,
            payload.L_max,
            payload.T,
            payload.comparar_pulp,
            payload.taxa_conversao,
        )
        if status == "UPDATE 0":
            await conn.execute(
                'INSERT INTO parametros_modelo '
                '("t", "LGD", "u_bar", "L_max", "T", "comparar_pulp", "taxa_conversao") '
                "VALUES ($1, $2, $3, $4, $5, $6, $7)",
                payload.t,
                payload.LGD,
                payload.u_bar,
                payload.L_max,
                payload.T,
                payload.comparar_pulp,
                payload.taxa_conversao,
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
    background_tasks: BackgroundTasks,
    usar_safra_existente: bool = False,
) -> ConsultaResponse:
    """
    Salva o parquet, resolve a safra, insere a consulta no banco
    e dispara o pipeline em background.

    Lança ValueError se safra_numero já existir e usar_safra_existente for False.
    """
    if Path(payload.nome_arquivo_parquet).name != payload.nome_arquivo_parquet:
        raise ValueError("Nome de arquivo invalido.")
    if not payload.nome_arquivo_parquet.lower().endswith(".parquet"):
        raise ValueError("Formato invalido. Envie um arquivo .parquet.")

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

    background_tasks.add_task(
        _pipeline_background,
        consulta_id,
        destino,
        payload.parametros.model_dump(),
    )

    return await get_consulta(UUID(consulta_id))


# ---------------------------------------------------------------------------
# Clusters
# ---------------------------------------------------------------------------


async def get_clusters(consulta_id: UUID) -> list[ClusterResultadoResponse] | None:
    """
    Retorna os clusters de uma consulta ordenados pelo segmento_id.
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
            SELECT segmento_id, n_clientes, pd_media, pi_media, cp_percentil5,
                   score_credito_cross_medio, ck_medio, fator_alavancagem,
                   limite_otimizado, limite_otimizado_pulp
            FROM clusters_resultado
            WHERE consulta_id = $1
            ORDER BY segmento_id ASC
            """,
            str(consulta_id),
        )

    return [
        ClusterResultadoResponse(
            segmento_id=row["segmento_id"],
            n_clientes=row["n_clientes"],
            pd_media=row["pd_media"],
            pi_media=row["pi_media"],
            cp_percentil5=row["cp_percentil5"],
            score_credito_cross_medio=row["score_credito_cross_medio"],
            ck_medio=row["ck_medio"],
            fator_alavancagem=row["fator_alavancagem"],
            limite_otimizado=row["limite_otimizado"],
            limite_otimizado_pulp=row["limite_otimizado_pulp"],
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

    df = await _carregar_clientes_consulta(consulta_id)
    if df is None:
        return []

    pagina = df.iloc[offset : offset + limit]
    return [_cliente_de_serie(consulta_id, s) for _, s in pagina.iterrows()]


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

    df = await _carregar_clientes_consulta(consulta_id)
    if df is None:
        return ""
    return _clientes_para_csv(consulta_id, df, incluir_pulp=False)


async def exportar_clientes_pulp_csv(consulta_id: UUID) -> str | None:
    """
    Retorna todos os clientes de uma consulta serializados como CSV,
    com a coluna limite_otimizado_pulp (vinda de clusters_resultado) adicionada.
    Retorna None se a consulta não existir.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        existe = await conn.fetchval(
            "SELECT 1 FROM consultas WHERE id = $1", str(consulta_id)
        )
        if not existe:
            return None

    df = await _carregar_clientes_consulta(consulta_id)
    if df is None:
        return ""
    # Consultas antigas (fallback na tabela) podem não ter limite_otimizado_pulp
    # no DataFrame; nesse caso buscamos por segmento em clusters_resultado.
    if "limite_otimizado_pulp" not in df.columns:
        pool = get_pool()
        async with pool.acquire() as conn:
            crows = await conn.fetch(
                "SELECT segmento_id, limite_otimizado_pulp "
                "FROM clusters_resultado WHERE consulta_id = $1",
                str(consulta_id),
            )
        mp = {r["segmento_id"]: r["limite_otimizado_pulp"] for r in crows}
        df = df.copy()
        df["limite_otimizado_pulp"] = df["segmento_id"].map(mp)
    return _clientes_para_csv(consulta_id, df, incluir_pulp=True)


async def calcular_z_banco(consulta_id: UUID) -> dict | None:
    """
    Calcula o valor da função objetivo usando os limites já concedidos pelo banco
    (coluna limite_ofertado). Clientes sem limite_ofertado (nulo) são tratados como 0.

    Fórmula (nível de cliente):
        z_banco = Σ_i [ π_i · (ū·t·T − PD_i·LGD) · limite_ofertado_i ]

    Retorna None se a consulta não existir.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        consulta = await conn.fetchrow(
            "SELECT parametros FROM consultas WHERE id = $1", str(consulta_id)
        )
    if not consulta:
        return None

    params = json.loads(consulta["parametros"])
    t, LGD, u_bar, T = params["t"], params["LGD"], params["u_bar"], params["T"]

    df = await _carregar_clientes_consulta(consulta_id)
    if df is None:
        return {"z_banco": 0.0, "n_com_oferta": 0, "n_total": 0}

    # z_banco = Σ_i [ pi_i · (ū·t·T − pd_calibrada_i·LGD) · limite_ofertado_i ],
    # com limite_ofertado nulo tratado como 0 (mesma fórmula da versão SQL).
    import numpy as _np

    pi = df["pi"].to_numpy(dtype="float64")
    pdc = df["pd_calibrada"].to_numpy(dtype="float64")
    lof = df["limite_ofertado"].to_numpy(dtype="float64")
    lof = _np.where(_np.isnan(lof), 0.0, lof)
    z_banco = float(_np.sum(pi * (u_bar * t * T - pdc * LGD) * lof))
    return {
        "z_banco": z_banco,
        "n_com_oferta": int((lof > 0).sum()),
        "n_total": int(len(df)),
    }


async def get_historico_cliente(token: int) -> ClienteHistoricoResponse | None:
    """
    Retorna o histórico de um cliente em todas as consultas em que apareceu,
    ordenado cronologicamente pela data de criação da consulta.
    Retorna None se o token não existir em nenhuma consulta.

    Fonte de verdade por cliente é o snapshot parquet de cada consulta
    (_RESULTADOS_DIR/{consulta_id}.parquet). Para consultas antigas sem
    snapshot, cai no fallback da tabela clientes_resultado.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        consultas = await conn.fetch(
            "SELECT id FROM consultas ORDER BY criado_em ASC"
        )

    historico: list[ClienteResultadoResponse] = []
    for c in consultas:
        cid = c["id"]
        p = _RESULTADOS_DIR / f"{cid}.parquet"
        if p.exists():
            # filtro empurrado pro parquet (lê só row groups com o token)
            sub = pd.read_parquet(p, filters=[("token", "==", int(token))])
            if len(sub) > 0:
                historico.append(_cliente_de_serie(UUID(str(cid)), sub.iloc[0]))
        else:
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM clientes_resultado "
                    "WHERE consulta_id = $1 AND token = $2",
                    cid,
                    token,
                )
            if row is not None:
                historico.append(_row_para_cliente(row))

    if not historico:
        return None

    return ClienteHistoricoResponse(token=token, historico=historico)


"""
Esta função é uma variante de criar_consulta() que recebe um Path já
existente em disco em vez de bytes, evitando ler o arquivo remontado
de volta para a memória após o upload em chunks.
"""


async def criar_consulta_de_path(
    payload: ConsultaCreate,
    parquet_path: Path,
    background_tasks: BackgroundTasks,
    usar_safra_existente: bool = False,
) -> ConsultaResponse:
    """
    Registra uma consulta no banco e dispara o pipeline em background
    a partir de um arquivo já presente em disco.

    Diferente de criar_consulta(), não recebe bytes nem grava o arquivo -
    assume que parquet_path já aponta para o arquivo final remontado.
    """
    if not parquet_path.name.lower().endswith(".parquet"):
        raise ValueError("Formato invalido. Envie um arquivo .parquet.")

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
            parquet_path.name,
            payload.parametros.model_dump_json(),
            "pendente",
            _agora(),
        )

    background_tasks.add_task(
        _pipeline_background,
        consulta_id,
        parquet_path,
        payload.parametros.model_dump(),
    )

    return await get_consulta(UUID(consulta_id))
