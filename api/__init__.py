from __future__ import annotations

from pathlib import Path

_BACKEND_API_DIR = Path(__file__).resolve().parents[1] / "apps" / "backend" / "api"

if _BACKEND_API_DIR.exists():
    __path__.append(str(_BACKEND_API_DIR))
