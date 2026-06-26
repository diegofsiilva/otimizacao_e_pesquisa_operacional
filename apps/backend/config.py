"""
backend/config.py

Configuração central do backend. Carrega variáveis de ambiente (de um arquivo
`.env` opcional ou do ambiente do processo) e expõe, como constantes de módulo,
todos os parâmetros usados pela aplicação: host/porta do backend, origens CORS
do frontend, diretórios de persistência local e credenciais do PostgreSQL.

Os valores são resolvidos uma única vez, no import do módulo, com defaults
seguros para desenvolvimento local. As funções auxiliares (`_*`) servem apenas
a essa resolução e não fazem parte da API pública do módulo.
"""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlsplit

BASE_DIR = Path(__file__).resolve().parent


def _load_env_file(path: Path) -> None:
    """Carrega um arquivo `.env` para o ambiente do processo, se ele existir.

    Cada linha no formato ``CHAVE=valor`` é adicionada via
    ``os.environ.setdefault`` — ou seja, variáveis já definidas no ambiente têm
    precedência e não são sobrescritas. Linhas em branco, comentários (``#``) e
    linhas sem ``=`` são ignoradas.

    Args:
        path: Caminho do arquivo `.env`. Se não existir, a função retorna sem
            efeito algum.

    Returns:
        None. O efeito é a mutação de ``os.environ``.
    """
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
    """Lê uma variável de ambiente com valores separados por vírgula.

    Args:
        name: Nome da variável de ambiente.
        default: Valor usado quando a variável não está definida.

    Returns:
        Lista de itens, já sem espaços nas bordas e sem entradas vazias.
    """
    raw = os.getenv(name, default)
    parts = raw.split(",")
    return [p.strip() for p in parts if p.strip()]


def _path_env(name: str, default: Path) -> Path:
    """Lê uma variável de ambiente como caminho de filesystem.

    Caminhos relativos são resolvidos a partir de ``BASE_DIR`` (a pasta do
    backend); caminhos absolutos são usados como estão.

    Args:
        name: Nome da variável de ambiente.
        default: Caminho usado quando a variável não está definida.

    Returns:
        O ``Path`` resolvido (sempre absoluto quando o default também é).
    """
    p = Path(os.getenv(name, str(default)))
    return p if p.is_absolute() else BASE_DIR / p


def _origin_with_port(base_url: str, port: int) -> str:
    """Monta uma origem CORS (``esquema://host:porta``) a partir de uma URL base.

    Preserva o esquema de ``base_url`` (default ``http``) e o host, trocando a
    porta pela informada. Usado para derivar a origem do frontend a partir de
    ``APP_HOST`` e ``FRONTEND_PORT``.

    Args:
        base_url: URL base do backend (ex.: ``http://127.0.0.1``).
        port: Porta do frontend a compor a origem.

    Returns:
        A origem normalizada (ex.: ``http://127.0.0.1:5500``).
    """
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

LOCAL_DATA_DIR = _path_env("LOCAL_DATA_DIR", BASE_DIR / "db" / "local_data")
UPLOAD_DIR = _path_env("UPLOAD_DIR", BASE_DIR / "uploads")
STATE_PATH = _path_env("STATE_PATH", LOCAL_DATA_DIR / "state.json")
PARAMS_PATH = _path_env("PARAMS_PATH", LOCAL_DATA_DIR / "params.json")

# ---------------------------------------------------------------------------
# PostgreSQL
# ---------------------------------------------------------------------------

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_DATABASE = os.getenv("DB_DATABASE", "")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
