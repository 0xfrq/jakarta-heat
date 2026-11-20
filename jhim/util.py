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


class PendingInputs(DataError):
    """Masukan hulu (mis. remote sensing Agent 1) belum tersedia; bukan kesalahan kode."""


def sha256(path, chunk: int = 1 << 20) -> str | None:
    import hashlib

    p = Path(path)
    if not p.exists():
        return None
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


# Generated analytical artefacts are expected to differ during and after a build.
# They do not make the *source* revision dirty; uncommitted source, config, input
# or documentation changes do.  Keep this list explicit and review it when a new
# generated output family is added.
GENERATED_PREFIXES = (
    "data/processed/modeling/",
    "data/processed/modeling_demo/",
    "data/processed/modeling_remediation/",
    "data/processed/integrated_comparisons/",
    "outputs/tables/",
    "outputs/figures/",
    "outputs/gis/",
    "outputs/remediation/",
    "outputs/qa/agent3/",
    "outputs/qa/rc1/",
    "outputs/qa/rc2/",
    "dist/",
    "cache/",
    ".venv/",
    ".pytest_cache/",
)


def _is_generated(path: str) -> bool:
    p = path.replace("\\", "/").lstrip("./")
    return any(p.startswith(prefix) for prefix in GENERATED_PREFIXES)


def git_source_state(root) -> dict:
    """Return HEAD and whether source (not generated artefacts) is uncommitted."""
    import subprocess

    result = {"commit": None, "revision": None, "state": "unknown", "dirty_paths": [], "generated_dirty_paths": []}
    try:
        head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10)
        if head.returncode != 0:
            return result
        commit = head.stdout.strip()
        status = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"],
                                capture_output=True, text=True, timeout=10)
        dirty, generated = [], []
        for line in status.stdout.splitlines():
            if not line.strip():
                continue
            path = line[3:].strip()
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            path = path.strip('"')
            (generated if _is_generated(path) else dirty).append(path)
        result.update({
            "commit": commit,
            "revision": commit + ("-dirty" if dirty else ""),
            "state": "dirty" if dirty else "clean",
            "dirty_paths": sorted(dirty),
            "generated_dirty_paths": sorted(generated),
        })
        return result
    except Exception:
        return result


def git_commit(root) -> str | None:
    return git_source_state(root)["revision"]


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
    out = {"python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__}
    for mod in ("geopandas", "libpysal", "esda", "scipy"):
        try:
            out[mod] = __import__(mod).__version__
        except Exception:
            pass
    return out


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
