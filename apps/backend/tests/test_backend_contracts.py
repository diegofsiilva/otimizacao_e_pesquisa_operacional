from __future__ import annotations

import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
ROUTES = BACKEND_DIR / "api" / "routes.py"
UPLOAD_ROUTES = BACKEND_DIR / "api" / "upload_routes.py"
CREDIT_SERVICE = BACKEND_DIR / "services" / "credit_service.py"


class BackendContractTestCase(unittest.TestCase):
    def test_endpoints_necessarios_para_o_frontend_estao_expostos(self) -> None:
        routes = ROUTES.read_text(encoding="utf-8")
        upload_routes = UPLOAD_ROUTES.read_text(encoding="utf-8")

        for rota in [
            '@router.get("/health")',
            '@router.get("/safras"',
            '@router.get("/consultas"',
            '@router.post("/consultas"',
            '@router.get("/consultas/{consulta_id}"',
            '"/consultas/{consulta_id}/clusters"',
            '"/consultas/{consulta_id}/clientes"',
            '"/consultas/{consulta_id}/clientes/export"',
            '@router.get("/clientes/{token}"',
            '@router.get("/config"',
            '@router.put("/config"',
        ]:
            self.assertIn(rota, routes)

        for rota in [
            '@router.post("/uploads/iniciar")',
            '@router.post("/uploads/{upload_id}/chunk")',
            '"/uploads/{upload_id}/finalizar"',
        ]:
            self.assertIn(rota, upload_routes)

    def test_upload_direto_repassa_confirmacao_de_safra_existente(self) -> None:
        routes = ROUTES.read_text(encoding="utf-8")

        self.assertIn("usar_safra_existente=usar_safra_existente", routes)

    def test_pipeline_roda_fora_da_event_loop_da_api(self) -> None:
        service = CREDIT_SERVICE.read_text(encoding="utf-8")

        self.assertIn("background_tasks.add_task", service)
        self.assertIn("asyncio.get_running_loop()", service)
        self.assertIn("run_in_executor", service)


if __name__ == "__main__":
    unittest.main()
