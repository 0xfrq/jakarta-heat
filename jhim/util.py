from __future__ import annotations

import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


class DataError(Exception):
    """Kesalahan struktur data: pemrosesan dihentikan dengan pesan yang jelas."""


def utf8_stdout() -> None:
    """Hindari UnicodeEncodeError di konsol/pengalihan Windows."""
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except Exception:
            pass


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def versions() -> dict:
    return {"python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__}


def _py(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return None if np.isnan(o) else float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, Path):
        return str(o)
    raise TypeError(f"tidak bisa diserialisasi: {type(o)}")


def write_json(path, obj) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=_py, allow_nan=False), encoding="utf-8")


def read_json(path) -> dict:
    p = Path(path)
    if not p.exists():
        raise DataError(f"Berkas tidak ditemukan: {p}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DataError(f"{p.name} bukan JSON yang sah: {exc}") from exc


def write_csv(df: pd.DataFrame, path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False, encoding="utf-8")
