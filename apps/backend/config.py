from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlsplit

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
    raw = os.getenv(name, default)
    parts = raw.split(",")
    return [p.strip() for p in parts if p.strip()]


def _path_env(name: str, default: Path) -> Path:
    p = Path(os.getenv(name, str(default)))
    return p if p.is_absolute() else BASE_DIR / p


def _origin_with_port(base_url: str, port: int) -> str:
    parsed = urlsplit(base_url)
    scheme = parsed.scheme or "http"
    host = parsed.hostname or base_url.split("://", 1)[-1].split(":", 1)[0]
    return f"{scheme}://{host}:{port}"


# ---------------------------------------------------------------------------
# Backend
# ---------------------------------------------------------------------------

# URL base do backend, incluindo protocolo (ex: http://127.0.0.1)
APP_HOST = os.getenv("APP_HOST", "http://127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", "8000"))

# Hostname/IP extraido para o bind do uvicorn (sem protocolo nem porta)
APP_HOST_BIND = APP_HOST.split("://", 1)[-1].split(":")[0]

# ---------------------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------------------

FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", "5500"))

# Origens CORS autorizadas a chamar a API.
#
# Em desenvolvimento local, derivadas automaticamente de APP_HOST e
# FRONTEND_PORT (ex: http://127.0.0.1:5500).
#
# Em producao com tunel ou dominio proprio, defina FRONTEND_ORIGINS no .env
# com a origem exata do frontend (ex: https://maiorais.com).
# Multiplas origens separadas por virgula sao suportadas.

_origins_env = os.getenv("FRONTEND_ORIGINS", "")

if _origins_env:
    # Usa o valor explicito do .env quando disponivel
    FRONTEND_ORIGINS = [o.strip() for o in _origins_env.split(",") if o.strip()]
else:
    # Fallback para desenvolvimento local
    if FRONTEND_PORT in (80, 443):
        FRONTEND_ORIGINS = [APP_HOST]
    else:
        local_origins = {_origin_with_port(APP_HOST, FRONTEND_PORT)}
        host = urlsplit(APP_HOST).hostname
        if host == "127.0.0.1":
            local_origins.add(f"http://localhost:{FRONTEND_PORT}")
        elif host == "localhost":
            local_origins.add(f"http://127.0.0.1:{FRONTEND_PORT}")
        FRONTEND_ORIGINS = sorted(local_origins)

# ---------------------------------------------------------------------------
# Persistencia local
# ---------------------------------------------------------------------------

_IS_VERCEL = bool(os.getenv("VERCEL"))
_DEFAULT_RUNTIME_DIR = Path("/tmp/g04") if _IS_VERCEL else BASE_DIR

LOCAL_DATA_DIR = _path_env(
    "LOCAL_DATA_DIR",
    _DEFAULT_RUNTIME_DIR / ("local_data" if _IS_VERCEL else "db/local_data"),
)
UPLOAD_DIR = _path_env(
    "UPLOAD_DIR",
    _DEFAULT_RUNTIME_DIR / ("uploads" if _IS_VERCEL else "uploads"),
)
STATE_PATH = _path_env("STATE_PATH", LOCAL_DATA_DIR / "state.json")
PARAMS_PATH = _path_env("PARAMS_PATH", LOCAL_DATA_DIR / "params.json")

# ---------------------------------------------------------------------------
# PostgreSQL
# ---------------------------------------------------------------------------

DB_URL = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or ""
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_DATABASE = os.getenv("DB_DATABASE", "")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_POOL_MIN_SIZE = int(os.getenv("DB_POOL_MIN_SIZE", "0" if _IS_VERCEL else "2"))
DB_POOL_MAX_SIZE = int(os.getenv("DB_POOL_MAX_SIZE", "1" if _IS_VERCEL else "10"))
DB_CONNECT_TIMEOUT = float(os.getenv("DB_CONNECT_TIMEOUT", "5"))
DB_STATEMENT_CACHE_SIZE = int(
    os.getenv("DB_STATEMENT_CACHE_SIZE", "0" if _IS_VERCEL else "100")
)
