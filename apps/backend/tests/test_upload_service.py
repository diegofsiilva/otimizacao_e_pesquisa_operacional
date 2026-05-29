from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from services import upload_service


class UploadServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.tmp.name)
        self.original_upload_dir = upload_service.UPLOAD_DIR
        self.original_chunks_dir = upload_service.CHUNKS_DIR
        upload_service.UPLOAD_DIR = self.base_dir / "uploads"
        upload_service.CHUNKS_DIR = upload_service.UPLOAD_DIR / "_chunks"

    def tearDown(self) -> None:
        upload_service.UPLOAD_DIR = self.original_upload_dir
        upload_service.CHUNKS_DIR = self.original_chunks_dir
        self.tmp.cleanup()

    def test_remonta_chunks_em_ordem_e_limpa_temporarios(self) -> None:
        sessao = upload_service.iniciar_upload("base.parquet")
        upload_id = sessao["upload_id"]

        upload_service.salvar_chunk(upload_id, 1, b"BBBB")
        upload_service.salvar_chunk(upload_id, 0, b"AAAA")

        destino = upload_service.finalizar_upload(upload_id)

        self.assertEqual(destino.name, "base.parquet")
        self.assertEqual(destino.read_bytes(), b"AAAABBBB")
        self.assertFalse((upload_service.CHUNKS_DIR / upload_id).exists())

    def test_recusa_extensao_nao_parquet(self) -> None:
        with self.assertRaisesRegex(ValueError, "parquet"):
            upload_service.iniciar_upload("base.csv")

    def test_recusa_nome_com_caminho(self) -> None:
        with self.assertRaisesRegex(ValueError, "Nome de arquivo"):
            upload_service.iniciar_upload("../base.parquet")


if __name__ == "__main__":
    unittest.main()
