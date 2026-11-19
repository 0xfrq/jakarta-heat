"""Pembacaan berkas hasil (dipakai skrip dan dashboard)."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from . import config as C
from .util import DataError, read_json, utf8_stdout


def read_csv_ids(path, name: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise DataError(f"{name} tidak ditemukan: {p}. Jalankan langkah sebelumnya dulu.")
    df = pd.read_csv(p, dtype={C.KEY: "string"})
    df[C.KEY] = df[C.KEY].astype(str)
    return df


def load_merged(paths: C.Paths):
    df = read_csv_ids(paths.merged, "merged_grid.csv")
    for col in ("valid",):
        if col not in df.columns:
            raise DataError("merged_grid.csv tidak memuat kolom 'valid'; jalankan ulang 03_prepare_model.py --merge")
        df[col] = df[col].astype(bool)
    return df, read_json(paths.merged_meta)


def load_priority(paths: C.Paths):
    df = read_csv_ids(paths.priority, "priority_models.csv")
    df["valid"] = df["valid"].astype(bool)
    for c in [c for c in df.columns if c.endswith("_top")]:
        df[c] = df[c].astype(bool)
    for c in [c for c in df.columns if c.endswith("_rank")]:
        df[c] = df[c].astype("Int64")
    return df, read_json(paths.priority_meta)


def run_cli(main) -> None:
    """Jalankan main(); DataError menjadi pesan singkat dan kode keluar 1 (bukan traceback panjang)."""
    utf8_stdout()
    try:
        main()
    except DataError as exc:
        print(f"\nGAGAL: {exc}", file=sys.stderr)
        sys.exit(1)
