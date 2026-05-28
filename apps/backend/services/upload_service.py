"""
services/upload_service.py
Gerenciamento de uploads em chunks para arquivos grandes.

Fluxo:
    1. POST /api/uploads/iniciar        -> cria diretório temporário, retorna upload_id
    2. POST /api/uploads/{id}/chunk     -> salva cada chunk no diretório
    3. POST /api/uploads/{id}/finalizar -> remonta o arquivo e retorna o Path final
"""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from config import UPLOAD_DIR

CHUNKS_DIR = UPLOAD_DIR / "_chunks"


def iniciar_upload(nome_arquivo: str) -> dict:
    """
    Cria um diretório temporário para receber os chunks.
    Retorna o upload_id que o cliente usará nas chamadas seguintes.
    """
    upload_id = str(uuid.uuid4())
    chunk_dir = CHUNKS_DIR / upload_id
    chunk_dir.mkdir(parents=True, exist_ok=True)
    (chunk_dir / "_nome").write_text(nome_arquivo, encoding="utf-8")
    return {"upload_id": upload_id}


def salvar_chunk(upload_id: str, index: int, dados: bytes) -> None:
    """
    Salva um chunk no diretório temporário do upload.
    O nome do arquivo é o índice zero-padded para garantir ordenação correta.
    """
    chunk_dir = CHUNKS_DIR / upload_id
    if not chunk_dir.exists():
        raise FileNotFoundError(f"Upload {upload_id} não encontrado.")
    (chunk_dir / f"{index:06d}").write_bytes(dados)


def finalizar_upload(upload_id: str) -> Path:
    """
    Remonta o arquivo a partir dos chunks salvos, em ordem de índice.
    Remove o diretório temporário após a remontagem.
    Retorna o Path do arquivo final em UPLOAD_DIR.
    """
    chunk_dir = CHUNKS_DIR / upload_id
    if not chunk_dir.exists():
        raise FileNotFoundError(f"Upload {upload_id} não encontrado.")

    nome = (chunk_dir / "_nome").read_text(encoding="utf-8")

    chunks = sorted(
        [f for f in chunk_dir.iterdir() if f.name != "_nome"],
        key=lambda f: int(f.name),
    )

    if not chunks:
        raise ValueError(f"Upload {upload_id} não contém nenhum chunk.")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    destino = UPLOAD_DIR / nome

    with open(destino, "wb") as out:
        for chunk in chunks:
            out.write(chunk.read_bytes())

    shutil.rmtree(chunk_dir, ignore_errors=True)

    return destino
