from __future__ import annotations

import atexit
import subprocess
import sys
from pathlib import Path

import uvicorn

from config import APP_HOST, APP_HOST_BIND, APP_PORT, FRONTEND_PORT

BACKEND_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BACKEND_DIR.parent / "frontend"


def _start_frontend() -> subprocess.Popen | None:
    if not FRONTEND_DIR.exists():
        print(f"[warn] frontend directory not found: {FRONTEND_DIR}")
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
