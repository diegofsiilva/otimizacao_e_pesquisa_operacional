from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd


BACKEND_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = BACKEND_DIR / "uploads"
STATE_PATH = BACKEND_DIR / "db" / "state.json"
PARAMS_PATH = BACKEND_DIR / "db" / "params.json"


def ensure_dirs() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default.copy()
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def _supabase_enabled() -> bool:
    return bool(os.getenv("SUPABASE_URL")) and bool(
        os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    )


def _supabase() -> Any:
    if not _supabase_enabled():
        return None
    from supabase import create_client

    url = os.environ["SUPABASE_URL"]
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.environ["SUPABASE_ANON_KEY"]
    return create_client(url, key)


def _kv_get(key: str) -> dict[str, Any] | None:
    client = _supabase()
    if client is None:
        return None
    response = client.table("app_kv").select("value").eq("key", key).limit(1).execute()
    data = getattr(response, "data", None) or []
    if not data:
        return None
    value = data[0].get("value")
    return value if isinstance(value, dict) else None


def _kv_set(key: str, value: dict[str, Any]) -> None:
    client = _supabase()
    if client is None:
        return
    client.table("app_kv").upsert({"key": key, "value": value}).execute()


def load_state() -> dict[str, Any]:
    default = {"last_upload": None, "last_result": None, "clusters": [], "n_clusters": 7}
    if _supabase_enabled():
        value = _kv_get("state")
        state = value if value is not None else default.copy()
    else:
        state = _read_json(STATE_PATH, default)

    # Backward-compat: versoes antigas usavam "clientes".
    if "clusters" not in state and "clientes" in state:
        state["clusters"] = state.get("clientes", [])
    return state


def save_state(state: dict[str, Any]) -> None:
    ensure_dirs()
    if _supabase_enabled():
        _kv_set("state", state)
        return
    _write_json(STATE_PATH, state)


def load_params() -> dict[str, Any]:
    default = {"t": 0.0175, "LGD": 0.8, "u_bar": 0.75, "L_max": 25000.0, "alpha": 0.05}
    if _supabase_enabled():
        value = _kv_get("params")
        return value if value is not None else default.copy()
    return _read_json(PARAMS_PATH, default)


def save_params(params: dict[str, Any]) -> None:
    ensure_dirs()
    if _supabase_enabled():
        _kv_set("params", params)
        return
    _write_json(PARAMS_PATH, params)


def read_dataframe(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    if suffix == ".parquet":
        return pd.read_parquet(path)
    raise ValueError("Formato nao suportado. Use CSV, XLSX, XLS ou parquet.")
