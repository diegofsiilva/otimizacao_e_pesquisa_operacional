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
    def __init__(self, conn):
        self.conn = conn

    async def __aenter__(self):
        return self.conn

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakeConnection:
    def __init__(self) -> None:
        self.executes = []
        self.executemany_calls = []
        self.copy_calls = []

    async def execute(self, sql, *args):
        self.executes.append((sql, args))
        return "UPDATE 1"

    async def executemany(self, sql, records):
        self.executemany_calls.append((sql, list(records)))

    async def copy_records_to_table(self, table, records, columns):
        self.copy_calls.append((table, list(records), list(columns)))


class FakePool:
    def __init__(self) -> None:
        self.conn = FakeConnection()

    def acquire(self):
        return FakeAcquire(self.conn)


@unittest.skipIf(IMPORT_ERROR is not None, f"dependencias indisponiveis: {IMPORT_ERROR}")
class PipelineBackgroundTestCase(unittest.TestCase):
    def test_pipeline_background_persiste_resultado_sem_bloquear_event_loop(self) -> None:
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
                        "cluster_id": 0,
                        "n_clientes": 1,
                        "pd_media": 0.02,
                        "pi_media": 0.5,
                        "cp_percentil5": 1000.0,
                        "score_credito_cross_medio": 700.0,
                        "ck_medio": 0.1,
                        "fator_alavancagem": 1.2,
                        "limite_otimizado": 500,
                    }
                ],
                "parquet_com_cluster": parquet_com_cluster,
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
                        "cluster_id": 0,
                    }
                ]
            )

            with (
                patch.object(credit_service, "get_pool", return_value=fake_pool),
                patch.object(credit_service, "_executar_pipeline", return_value=resultado_pipeline),
                patch.object(credit_service.pd, "read_parquet", return_value=clientes),
                patch.object(pq, "read_metadata", return_value=SimpleNamespace(num_rows=1)),
            ):
                asyncio.run(
                    credit_service._pipeline_background(
                        consulta_id,
                        parquet_path,
                        {"t": 0.0175, "LGD": 0.8, "u_bar": 0.75, "L_max": 25000, "T": 22},
                    )
                )

        executed_sql = "\n".join(sql for sql, _ in fake_pool.conn.executes)
        self.assertIn("status_consulta = $1", executed_sql)
        self.assertIn("z_otimo", executed_sql)
        self.assertEqual(fake_pool.conn.executemany_calls[0][1][0][0], consulta_id)
        self.assertEqual(fake_pool.conn.copy_calls[0][0], "clientes_resultado")
        self.assertEqual(fake_pool.conn.copy_calls[0][1][0][-1], 500)


if __name__ == "__main__":
    unittest.main()
