from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from config import LOCAL_DATA_DIR, PARAMS_PATH, STATE_PATH, UPLOAD_DIR


def ensure_dirs() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    LOCAL_DATA_DIR.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default.copy()
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def load_state() -> dict[str, Any]:
    default = {"last_upload": None, "last_result": None, "clusters": [], "n_clusters": 7}
    state = _read_json(STATE_PATH, default)

    return state


def save_state(state: dict[str, Any]) -> None:
    ensure_dirs()
    _write_json(STATE_PATH, state)


def load_params() -> dict[str, Any]:
    default = {"t": 0.0175, "LGD": 0.8, "u_bar": 0.75, "L_max": 25000.0, "alpha": 0.05}
    return _read_json(PARAMS_PATH, default)

def save_params(params: dict[str, Any]) -> None:
    ensure_dirs()
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
