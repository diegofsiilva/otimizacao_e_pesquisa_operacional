from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_env_file(BASE_DIR / ".env")


def _csv_env(name: str, default: str) -> list[str]:
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


def _path_env(name: str, default: Path) -> Path:
    value = Path(os.getenv(name, str(default)))
    return value if value.is_absolute() else BASE_DIR / value


APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
FRONTEND_ORIGINS = _csv_env("FRONTEND_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")

LOCAL_DATA_DIR = _path_env("LOCAL_DATA_DIR", BASE_DIR / "db" / "local_data")
UPLOAD_DIR = _path_env("UPLOAD_DIR", BASE_DIR / "uploads")
STATE_PATH = _path_env("STATE_PATH", LOCAL_DATA_DIR / "state.json")
PARAMS_PATH = _path_env("PARAMS_PATH", LOCAL_DATA_DIR / "params.json")
