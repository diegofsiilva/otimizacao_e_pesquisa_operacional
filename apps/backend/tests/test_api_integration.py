"""
backend/tests/test_api_integration.py

Testes de integração HTTP da API, usando o ``TestClient`` do FastAPI (sem subir
servidor nem banco). Cobrem o health check, o upload direto e o upload em chunks
(com a camada de serviço mockada), além das validações de formato, nome de
arquivo e parâmetros de query. Toda a suíte é pulada quando as dependências do
backend não estão instaladas.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, patch
from urllib import response
from uuid import uuid4


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


try:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from api import routes, upload_routes
    from model.schemas import ConsultaResponse, ParametrosModelo
    from services import upload_service
except ModuleNotFoundError as exc:  # pragma: no cover - ambiente sem dependencias
    FastAPI = None
    TestClient = None
    routes = None
    upload_routes = None
    ConsultaResponse = None
    ParametrosModelo = None
    upload_service = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


def _consulta_response(nome_arquivo: str = "base.parquet"):
    """Cria um ``ConsultaResponse`` de exemplo para os mocks de serviço.

    Args:
        nome_arquivo: Nome do parquet a registrar na resposta.

    Returns:
        Um ``ConsultaResponse`` com IDs aleatórios e status ``"pendente"``.
    """
    return ConsultaResponse(
        id=uuid4(),
        safra_id=uuid4(),
        nome_arquivo_parquet=nome_arquivo,
        parametros=ParametrosModelo(),
        status_consulta="pendente",
        criado_em=datetime.now(timezone.utc),
    )


@unittest.skipIf(IMPORT_ERROR is not None, f"dependencias indisponiveis: {IMPORT_ERROR}")
class ApiIntegrationTestCase(unittest.TestCase):
    """Testes de integração HTTP das rotas da API via TestClient."""

    def setUp(self) -> None:
        """Monta um app FastAPI com as rotas e cria um TestClient isolado."""
        app = FastAPI()
        app.include_router(routes.router, prefix="/api")
        app.include_router(upload_routes.router, prefix="/api")
        self.client = TestClient(app)

    def test_health_endpoint_responde_sem_banco(self) -> None:
        """O /health deve responder 200 com ``{"status": "ok"}`` sem depender de banco."""
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_upload_direto_cria_consulta_e_repassa_safra_existente(self) -> None:
        """Upload direto deve criar consulta (201) e repassar safra/flags/parâmetros ao serviço."""
        captured = {}

        async def fake_criar_consulta(payload, conteudo, background_tasks, usar_safra_existente=False):
            """Mock de ``criar_consulta``: captura os argumentos e devolve uma resposta fake."""
            captured["payload"] = payload
            captured["conteudo"] = conteudo
            captured["usar_safra_existente"] = usar_safra_existente
            return _consulta_response(payload.nome_arquivo_parquet)

        with patch.object(routes, "criar_consulta", new=AsyncMock(side_effect=fake_criar_consulta)):
            response = self.client.post(
                "/api/consultas?safra_numero=3&usar_safra_existente=true&t=0.02",
                files={"file": ("base.parquet", b"parquet-bytes", "application/octet-stream")},
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["nome_arquivo_parquet"], "base.parquet")
        self.assertEqual(captured["conteudo"], b"parquet-bytes")
        self.assertTrue(captured["usar_safra_existente"])
        self.assertEqual(captured["payload"].safra_numero, 3)
        self.assertAlmostEqual(captured["payload"].parametros.t, 0.02)

    def test_upload_direto_recusa_formato_invalido(self) -> None:
        """Upload de arquivo não-``.parquet`` deve retornar 400 com mensagem sobre parquet."""
        response = self.client.post(
            "/api/consultas",
            files={"file": ("base.csv", b"csv", "text/csv")},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("parquet", response.json()["detail"])

    def test_fluxo_http_de_upload_em_chunks_dispara_consulta(self) -> None:
        """Fluxo iniciar→chunks→finalizar deve remontar o arquivo e disparar a consulta (201)."""
        captured = {}

        async def fake_criar_consulta_de_path(payload, parquet_path, background_tasks, usar_safra_existente=False):
            """Mock de ``criar_consulta_de_path``: captura os argumentos e devolve resposta fake."""
            captured["payload"] = payload
            captured["parquet_path"] = parquet_path
            captured["usar_safra_existente"] = usar_safra_existente
            return _consulta_response(parquet_path.name)

        with tempfile.TemporaryDirectory() as tmp:
            original_upload_dir = upload_service.UPLOAD_DIR
            original_chunks_dir = upload_service.CHUNKS_DIR
            upload_service.UPLOAD_DIR = Path(tmp) / "uploads"
            upload_service.CHUNKS_DIR = upload_service.UPLOAD_DIR / "_chunks"

            try:
                with patch.object(
                    upload_routes,
                    "criar_consulta_de_path",
                    new=AsyncMock(side_effect=fake_criar_consulta_de_path),
                ):
                    iniciar = self.client.post(
                        "/api/uploads/iniciar?nome_arquivo=base.parquet"
                    )
                    self.assertEqual(iniciar.status_code, 200)
                    upload_id = iniciar.json()["upload_id"]

                    chunk0 = self.client.post(
                        f"/api/uploads/{upload_id}/chunk?index=0",
                        files={"file": ("chunk", b"AAAA", "application/octet-stream")},
                    )
                    chunk1 = self.client.post(
                        f"/api/uploads/{upload_id}/chunk?index=1",
                        files={"file": ("chunk", b"BBBB", "application/octet-stream")},
                    )
                    self.assertEqual(chunk0.status_code, 200)
                    self.assertEqual(chunk1.status_code, 200)

                    finalizar = self.client.post(
                        f"/api/uploads/{upload_id}/finalizar?usar_safra_existente=true&LGD=0.7"
                    )

                self.assertEqual(finalizar.status_code, 201)
                self.assertEqual(finalizar.json()["nome_arquivo_parquet"], "base.parquet")
                self.assertEqual(captured["parquet_path"].read_bytes(), b"AAAABBBB")
                self.assertTrue(captured["usar_safra_existente"])
                self.assertAlmostEqual(captured["payload"].parametros.LGD, 0.7)
            finally:
                upload_service.UPLOAD_DIR = original_upload_dir
                upload_service.CHUNKS_DIR = original_chunks_dir
    
    def test_upload_em_chunks_retorna_404_quando_upload_id_nao_existe(self) -> None:
        """Enviar chunk para um upload_id inexistente deve retornar 404."""
        response = self.client.post(
            "/api/uploads/id-inexistente/chunk?index=0",
            files={"file": ("chunk", b"AAAA", "application/octet-stream")},
        )
        self.assertEqual(response.status_code, 404)

    def test_upload_direto_recusa_nome_de_arquivo_com_caminho(self) -> None:
        """Upload com nome contendo caminho (``../``) deve retornar 400."""
        response = self.client.post(
            "/api/consultas",
            files={"file": ("../base.parquet", b"parquet-bytes", "application/octet-stream")},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Nome de arquivo", response.json()["detail"])

    def test_validacao_query_param_retorna_422_quando_LGD_invalido(self) -> None:
        """LGD fora do intervalo válido (>1) deve disparar validação 422 do FastAPI."""
        response = self.client.post(
            "/api/consultas?LGD=1.5",
            files={"file": ("base.parquet", b"parquet-bytes", "application/octet-stream")},
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
