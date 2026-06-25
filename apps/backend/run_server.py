"""
backend/run_server.py

Ponto de entrada para subir backend e frontend juntos em desenvolvimento.

Executado diretamente (``python run_server.py``), o script:
  1. sobe o frontend estático em ``http.server`` na ``FRONTEND_PORT``, gerando
     antes o ``runtime-config.js`` com a URL da API;
  2. imprime as URLs de frontend, backend e docs;
  3. sobe a API FastAPI via uvicorn com reload.

O frontend é opcional: se a porta estiver ocupada, o diretório não existir ou o
processo morrer no startup, o backend sobe mesmo assim (com avisos). As funções
auxiliares (`_*`) cuidam de cada etapa e não compõem uma API pública.
"""

from __future__ import annotations

import atexit
import json
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from config import APP_HOST, APP_HOST_BIND, APP_PORT, FRONTEND_PORT

BACKEND_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BACKEND_DIR.parent / "frontend"
RUNTIME_CONFIG_PATH = FRONTEND_DIR / "runtime-config.js"
FRONTEND_STARTUP_TIMEOUT_SECONDS = 0.5


def _backend_api_url() -> str:
    """Monta a URL pública da API a partir de ``APP_HOST``/``APP_PORT``.

    Returns:
        A URL completa com o sufixo ``/api`` (ex.: ``http://127.0.0.1:8000/api``),
        usada para escrever o ``runtime-config.js`` consumido pelo frontend.
    """
    parsed = urlsplit(APP_HOST)
    scheme = parsed.scheme or "http"
    host = parsed.hostname or APP_HOST.split("://", 1)[-1].split(":", 1)[0]
    port = parsed.port or APP_PORT
    netloc = f"{host}:{port}"
    return urlunsplit((scheme, netloc, "/api", "", ""))


def _write_frontend_runtime_config() -> None:
    """Gera o ``runtime-config.js`` do frontend com a URL atual da API.

    Sobrescreve o arquivo definindo ``window.API_BASE_URL``, de modo que o
    frontend estático aponte para o backend correto sem edição manual.

    Returns:
        None. O efeito é a escrita do arquivo em ``RUNTIME_CONFIG_PATH``.
    """
    api_url = _backend_api_url()
    RUNTIME_CONFIG_PATH.write_text(
        "window.API_BASE_URL = " + json.dumps(api_url) + ";\n",
        encoding="utf-8",
    )


def _frontend_url() -> str:
    """Retorna a URL do frontend (``APP_HOST`` + ``FRONTEND_PORT``), só para exibição."""
    return f"{APP_HOST}:{FRONTEND_PORT}"


def _is_port_available(host: str, port: int) -> bool:
    """Verifica se uma porta TCP está livre para bind.

    Args:
        host: Host/IP onde tentar o bind.
        port: Porta TCP a testar.

    Returns:
        ``True`` se o bind teve sucesso (porta livre); ``False`` se a porta já
        está em uso (``OSError`` no bind).
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((host, port))
    except OSError:
        return False
    return True


def _start_frontend() -> subprocess.Popen | None:
    """Sobe o servidor estático do frontend em um subprocesso.

    Faz as verificações de pré-condição (diretório existe, porta livre), grava o
    ``runtime-config.js`` e lança ``python -m http.server`` apontando para a
    pasta do frontend. Registra ``terminate`` em ``atexit`` para encerrar o
    subprocesso junto com o backend.

    Returns:
        O ``subprocess.Popen`` do servidor em caso de sucesso, ou ``None`` se o
        frontend não pôde ser iniciado (diretório ausente, porta ocupada, falha
        ao escrever config ou processo que morreu no startup). Em todos os casos
        de ``None`` um aviso é impresso e o backend segue normalmente.
    """
    if not FRONTEND_DIR.exists():
        print(f"[warn] frontend directory not found: {FRONTEND_DIR}")
        return None

    if not _is_port_available(APP_HOST_BIND, FRONTEND_PORT):
        print(
            f"[warn] frontend not started: port {FRONTEND_PORT} is already in use "
            f"on {APP_HOST_BIND}."
        )
        print("       Change FRONTEND_PORT in apps/backend/.env or stop the other process.")
        return None

    try:
        _write_frontend_runtime_config()
    except OSError as exc:
        print(f"[warn] frontend runtime config could not be written: {exc}")
        return None

    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "http.server",
            str(FRONTEND_PORT),
            "--bind",
            APP_HOST_BIND,
            "--directory",
            str(FRONTEND_DIR),
        ],
        stdout=subprocess.DEVNULL,
        stderr=None,
    )

    time.sleep(FRONTEND_STARTUP_TIMEOUT_SECONDS)
    if proc.poll() is not None:
        print(f"[warn] frontend server exited during startup: {_frontend_url()}")
        return None

    atexit.register(proc.terminate)
    return proc


def _print_urls(frontend_ok: bool) -> None:
    """Imprime no console as URLs de acesso ao sistema.

    Args:
        frontend_ok: Quando ``True``, inclui a URL do frontend; quando ``False``
            (frontend não iniciado), exibe apenas backend e docs.

    Returns:
        None.
    """
    print()
    print("  Sistema de Credito Banco PAN")
    print()
    if frontend_ok:
        print(f"  Frontend: {_frontend_url()}")
    print(f"  Backend:  {APP_HOST}:{APP_PORT}")
    print(f"  Docs:     {APP_HOST}:{APP_PORT}/docs")
    print()


if __name__ == "__main__":
    import uvicorn

    frontend_proc = _start_frontend()
    _print_urls(frontend_ok=frontend_proc is not None)

    uvicorn.run(
        "main:app",
        host=APP_HOST_BIND,
        port=APP_PORT,
        reload=True,
        reload_dirs=[str(BACKEND_DIR)],
        app_dir=str(BACKEND_DIR),
    )
