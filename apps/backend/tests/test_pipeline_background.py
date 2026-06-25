"""
backend/tests/test_pipeline_background.py

Teste de integração do pipeline executado em background
(``credit_service._pipeline_background``). Usa fakes de pool/conexão asyncpg e
mocks do pipeline pesado para verificar, sem banco real, que o resultado é
persistido (snapshot em parquet por consulta + UPDATE de status) sem bloquear a
event loop. As classes ``Fake*`` simulam a interface mínima do driver de banco.
"""

from __future__ import annotations

import asyncio
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


try:
    import pandas as pd
    import pyarrow.parquet as pq

    from services import credit_service
except ModuleNotFoundError as exc:  # pragma: no cover - ambiente sem dependencias
    pd = None
    pq = None
    credit_service = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


class FakeAcquire:
    """Context manager assíncrono que simula ``pool.acquire()`` do asyncpg."""

    def __init__(self, conn):
        """Guarda a conexão fake a ser devolvida ao entrar no contexto."""
        self.conn = conn

    async def __aenter__(self):
        """Entra no contexto async e devolve a conexão fake."""
        return self.conn

    async def __aexit__(self, exc_type, exc, tb):
        """Sai do contexto sem suprimir exceções (retorna ``False``)."""
        return False


class FakeConnection:
    """Conexão fake que registra as chamadas SQL em vez de tocar em um banco real."""

    def __init__(self) -> None:
        """Inicializa as listas que acumulam as chamadas recebidas."""
        self.executes = []
        self.executemany_calls = []
        self.copy_calls = []

    async def execute(self, sql, *args):
        """Registra um ``execute`` e devolve uma tag de comando fixa.

        Args:
            sql: Comando SQL recebido.
            *args: Parâmetros posicionais do comando.

        Returns:
            A string ``"UPDATE 1"``, imitando a tag de status do asyncpg.
        """
        self.executes.append((sql, args))
        return "UPDATE 1"

    async def executemany(self, sql, records):
        """Registra uma chamada ``executemany`` (SQL + registros materializados)."""
        self.executemany_calls.append((sql, list(records)))

    async def copy_records_to_table(self, table, records, columns):
        """Registra uma chamada de ``copy_records_to_table`` (tabela, registros, colunas)."""
        self.copy_calls.append((table, list(records), list(columns)))


class FakePool:
    """Pool fake que entrega sempre a mesma ``FakeConnection`` via ``acquire()``."""

    def __init__(self) -> None:
        """Cria a conexão fake compartilhada pelo pool."""
        self.conn = FakeConnection()

    def acquire(self):
        """Retorna um :class:`FakeAcquire` em torno da conexão fake."""
        return FakeAcquire(self.conn)


@unittest.skipIf(IMPORT_ERROR is not None, f"dependencias indisponiveis: {IMPORT_ERROR}")
class PipelineBackgroundTestCase(unittest.TestCase):
    """Testa a persistência do resultado do pipeline executado em background."""

    def test_pipeline_background_persiste_resultado_sem_bloquear_event_loop(self) -> None:
        """O pipeline em background deve gravar o snapshot parquet e atualizar o status no banco."""
        fake_pool = FakePool()
        consulta_id = "consulta-1"

        with tempfile.TemporaryDirectory() as tmp:
            parquet_path = Path(tmp) / "base.parquet"
            parquet_path.write_bytes(b"fixture")
            parquet_com_cluster = Path(tmp) / "base_com_cluster.parquet"

            resultado_pipeline = {
                "status": "otimo",
                "z": 123.45,
                "clusters": [
                    {
                        "segmento_id": 0,
                        "n_clientes": 1,
                        "pd_media": 0.02,
                        "pi_media": 0.5,
                        "cp_percentil5": 1000.0,
                        "score_credito_cross_medio": 700.0,
                        "ck_medio": 0.1,
                        "fator_alavancagem": 1.2,
                        "limite_otimizado": 500,
                        "limite_otimizado_pulp": 500,
                    }
                ],
                "parquet_com_cluster": parquet_com_cluster,
                "z_pulp": 123.45,
                "status_pulp": "otimo",
                "delta_z_pct": 0.0,
            }

            clientes = pd.DataFrame(
                [
                    {
                        "token": 1,
                        "safra_ref_uso": "M1",
                        "score_interno": 800,
                        "pd_produto": 0.02,
                        "score_generico_1": None,
                        "score_generico_2": None,
                        "capacidade_pagamento": 1000.0,
                        "delta_capacidade_pagamento": 0.0,
                        "score_propensao_contrato": 0.5,
                        "score_credito_cross": 700,
                        "renda_estimada": 5000.0,
                        "fx_idade": "26-35",
                        "limite_ofertado": None,
                        "flag_contrato": 1,
                        "flag_ativacao": 1,
                        "over30mob3": None,
                        "pd_calibrada": 0.02,
                        "pi": 0.5,
                        "cp_proxy": 1000.0,
                        "segmento_id": 0,
                    }
                ]
            )

            with (
                patch.object(credit_service, "get_pool", return_value=fake_pool),
                patch.object(credit_service, "_executar_pipeline", return_value=resultado_pipeline),
                patch.object(credit_service.pd, "read_parquet", return_value=clientes),
                patch.object(pq, "read_metadata", return_value=SimpleNamespace(num_rows=1)),
                patch.object(
                    credit_service, "_RESULTADOS_DIR", Path(tmp) / "resultados"
                ),
            ):
                asyncio.run(
                    credit_service._pipeline_background(
                        consulta_id,
                        parquet_path,
                        {"t": 0.0175, "LGD": 0.8, "u_bar": 0.75, "L_max": 25000, "T": 22},
                    )
                )

            # snapshot por consulta gravado como parquet (substitui o COPY de
            # ~1.8M linhas que ia para clientes_resultado)
            resultado_parquet = (
                Path(tmp) / "resultados" / f"{consulta_id}.parquet"
            )
            self.assertTrue(resultado_parquet.exists())
            snap = pd.read_parquet(resultado_parquet)
            self.assertEqual(int(snap.iloc[0]["limite_otimizado"]), 500)
            self.assertEqual(int(snap.iloc[0]["limite_otimizado_pulp"]), 500)

        executed_sql = "\n".join(sql for sql, _ in fake_pool.conn.executes)
        self.assertIn("status_consulta = $1", executed_sql)
        self.assertIn("z_otimo", executed_sql)
        self.assertEqual(fake_pool.conn.executemany_calls[0][1][0][0], consulta_id)


if __name__ == "__main__":
    unittest.main()
