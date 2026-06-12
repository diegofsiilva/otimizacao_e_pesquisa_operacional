from __future__ import annotations

import atexit
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import uvicorn

from config import APP_HOST, APP_HOST_BIND, APP_PORT, FRONTEND_PORT

BACKEND_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BACKEND_DIR.parent / "frontend"
RUNTIME_CONFIG_PATH = FRONTEND_DIR / "runtime-config.js"


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


def _start_frontend() -> subprocess.Popen | None:
    if not FRONTEND_DIR.exists():
        print(f"[warn] frontend directory not found: {FRONTEND_DIR}")
        return None

    _write_frontend_runtime_config()

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
        stderr=subprocess.DEVNULL,
    )
    atexit.register(proc.terminate)
    return proc


def _print_urls(frontend_ok: bool) -> None:
    print()
    print("  Sistema de Credito Banco PAN")
    print()
    if frontend_ok:
        print(f"  Frontend: {APP_HOST}:{FRONTEND_PORT}")
    print(f"  Backend:  {APP_HOST}:{APP_PORT}")
    print(f"  Docs:     {APP_HOST}:{APP_PORT}/docs")
    print()


if __name__ == "__main__":
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
