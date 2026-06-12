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

    def test_salvar_chunk_upload_inexistente_dispara_file_not_found(self) -> None:
        with self.assertRaisesRegex(FileNotFoundError, "não encontrado"):
            upload_service.salvar_chunk("nao-existe", 0, b"AAAA")

    def test_finalizar_upload_upload_inexistente_dispara_file_not_found(self) -> None:
        with self.assertRaisesRegex(FileNotFoundError, "não encontrado"):
            upload_service.finalizar_upload("nao-existe")

    def test_finalizar_upload_sem_chunks_recusa(self) -> None:
        sessao = upload_service.iniciar_upload("base.parquet")
        upload_id = sessao["upload_id"]

        with self.assertRaisesRegex(ValueError, "nenhum chunk"):
            upload_service.finalizar_upload(upload_id)

    def test_aceita_extensao_parquet_em_maiusculo(self) -> None:
        sessao = upload_service.iniciar_upload("BASE.PARQUET")
        upload_id = sessao["upload_id"]

        upload_service.salvar_chunk(upload_id, 0, b"OK")
        destino = upload_service.finalizar_upload(upload_id)

        self.assertEqual(destino.name, "BASE.PARQUET")
        self.assertEqual(destino.read_bytes(), b"OK")

    def test_recusa_nome_com_barra_invertida_windows(self) -> None:
        if sys.platform != "win32":
            self.skipTest("Separador invertido é específico do Windows")

        with self.assertRaisesRegex(ValueError, "Nome de arquivo"):
            upload_service.iniciar_upload(r"pastas\base.parquet")


if __name__ == "__main__":
    unittest.main()
