"""Empat model prioritas panas (M1-M4): komponen, skor, peringkat.

Semua komponen berskala 0-1 dengan arah sama (tinggi = lebih prioritas).
Peringkat 1 = prioritas tertinggi; seri dipecah menurut grid_id sehingga hasil
tidak bergantung pada urutan baris.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from . import config as C


def norm01(x: pd.Series, clip=C.NORM_CLIP) -> pd.Series:
    """Min-max setelah dipotong pada persentil `clip`; clip=None memberi min-max murni."""
    x = pd.Series(x, dtype=float)
    v = x.dropna()
    if v.empty:
        return x
    lo, hi = (v.quantile(clip[0]), v.quantile(clip[1])) if clip else (v.min(), v.max())
    if not hi > lo:
        return pd.Series(0.5, index=x.index).where(x.notna())
    return ((x - lo) / (hi - lo)).clip(0.0, 1.0)


def components(
    df: pd.DataFrame,
    clip=C.NORM_CLIP,
    park_mode: str = "continuous",
    park_cap: float = C.PARK_CAP_M,
    park_thr: float | None = None,
) -> pd.DataFrame:
    """Komponen 0-1 untuk grid VALID.

    lst, ndvi_low, pop, vuln dinormalisasi min-max terpotong (populasi pada skala log1p).
    park_deficit: "continuous" = min(jarak, cap)/cap; "binary" = 1 jika jarak > park_thr.
    """
    c = pd.DataFrame(index=df.index)
    c["lst"] = norm01(df["lst_c"], clip)
    c["ndvi_low"] = 1.0 - norm01(df["ndvi"], clip)
    c["pop"] = norm01(np.log1p(df["population"]), clip)
    c["vuln"] = norm01(np.log1p(df["pop_child"] + df["pop_elderly"]), clip)
    d = df["park_distance_m"]
    if park_mode == "continuous":
        c["park_deficit"] = d.clip(lower=0, upper=park_cap) / park_cap
    elif park_mode == "binary":
        if park_thr is None:
            raise ValueError("park_thr wajib untuk park_mode='binary'")
        c["park_deficit"] = (d > park_thr).astype(float).where(d.notna())
    else:
        raise ValueError("park_mode harus 'continuous' atau 'binary'")
    return c


def normalize_weights(w: dict[str, float]) -> dict[str, float]:
    if not w or any((not np.isfinite(v)) or v < 0 for v in w.values()) or sum(w.values()) <= 0:
        raise ValueError("Bobot harus non-negatif dengan jumlah > 0.")
    s = float(sum(w.values()))
    return {k: float(v) / s for k, v in w.items()}


def weighted_score(comp: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    w = normalize_weights(weights)
    missing = [k for k in w if k not in comp.columns]
    if missing:
        raise ValueError(f"Komponen tidak ada: {missing}")
    return sum(comp[k] * v for k, v in w.items())


def rank_desc(score: pd.Series, tiebreak: pd.Series, secondary: pd.Series | None = None) -> pd.Series:
    """Peringkat 1 = skor tertinggi. Seri dipecah oleh `secondary` (turun), lalu tiebreak/grid_id (naik)."""
    s = np.asarray(score, dtype=float)
    k = np.asarray(tiebreak, dtype=str)
    sec = np.zeros(len(s)) if secondary is None else np.asarray(secondary, dtype=float)
    order = np.lexsort((k, -sec, -s))
    r = np.empty(len(s), dtype=int)
    r[order] = np.arange(1, len(s) + 1)
    return pd.Series(r, index=score.index)


def score_rank(v: pd.DataFrame, weights: dict[str, float], clip=C.NORM_CLIP, **comp_kw):
    """Skor dan peringkat untuk grid valid v.

    Pemotongan persentil (clip) membuat banyak grid di ekor atas bernilai sama (=1). Agar peringkat
    tidak ditentukan oleh grid_id, seri dipecah dahulu oleh skor tanpa pemotongan (min-max murni).
    """
    s = weighted_score(components(v, clip=clip, **comp_kw), weights)
    raw = weighted_score(components(v, clip=None, **comp_kw), weights) if clip else s
    return s, rank_desc(s, v[C.KEY], secondary=raw)


def n_top(n_valid: int, frac: float = C.TOP_FRAC) -> int:
    return int(math.ceil(frac * n_valid)) if n_valid > 0 else 0


def top_mask(rank: pd.Series, n_valid: int, frac: float = C.TOP_FRAC) -> pd.Series:
    return (rank <= n_top(n_valid, frac)).fillna(False).astype(bool)


def build_priority_table(
    df: pd.DataFrame,
    models: dict[str, dict[str, float]] = C.MODELS,
    top_frac: float = C.TOP_FRAC,
    clip=C.NORM_CLIP,
    park_cap: float = C.PARK_CAP_M,
) -> pd.DataFrame:
    """Skor, peringkat, dan penanda top-N semua model pada SATU set grid valid yang sama.

    df: keluaran data.clean_values (harus punya kolom `valid`).
    """
    if "valid" not in df.columns:
        raise ValueError("df harus berasal dari data.clean_values (kolom 'valid').")
    v = df.loc[df["valid"]]
    out = pd.DataFrame({C.KEY: df[C.KEY].to_numpy()}, index=df.index)
    out["valid"] = df["valid"].to_numpy()
    if v.empty:
        raise ValueError("Tidak ada grid valid; periksa tabel kualitas data.")
    comp = components(v, clip=clip, park_cap=park_cap)  # hanya untuk kolom komponen (c_*)
    for name, col in (("lst", "c_lst"), ("ndvi_low", "c_ndvi_low"), ("pop", "c_pop"),
                      ("vuln", "c_vuln"), ("park_deficit", "c_park")):
        out[col] = comp[name].reindex(df.index)
    nv = len(v)
    for m, w in models.items():
        k = m.lower()
        s, r = score_rank(v, w, clip=clip, park_cap=park_cap)
        out[f"{k}_score"] = s.reindex(df.index)
        out[f"{k}_rank"] = r.reindex(df.index).astype("Int64")
        out[f"{k}_top"] = top_mask(out[f"{k}_rank"], nv, top_frac)
    return out.reset_index(drop=True)
