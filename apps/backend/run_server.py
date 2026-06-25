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
    parsed = urlsplit(APP_HOST)
    scheme = parsed.scheme or "http"
    host = parsed.hostname or APP_HOST.split("://", 1)[-1].split(":", 1)[0]
    port = parsed.port or APP_PORT
    netloc = f"{host}:{port}"
    return urlunsplit((scheme, netloc, "/api", "", ""))


def _write_frontend_runtime_config() -> None:
    api_url = _backend_api_url()
    RUNTIME_CONFIG_PATH.write_text(
        "window.API_BASE_URL = " + json.dumps(api_url) + ";\n",
        encoding="utf-8",
    )


def _frontend_url() -> str:
    return f"{APP_HOST}:{FRONTEND_PORT}"


def _is_port_available(host: str, port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((host, port))
    except OSError:
        return False
    return True


def _start_frontend() -> subprocess.Popen | None:
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
