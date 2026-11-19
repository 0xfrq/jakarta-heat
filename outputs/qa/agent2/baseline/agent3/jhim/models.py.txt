"""Empat model prioritas panas (M1-M4): komponen, skor, peringkat, kelas.

Semua komponen berskala 0-1 dengan arah sama (tinggi = lebih prioritas).
Peringkat 1 = prioritas tertinggi; seri dipecah oleh skor tanpa pemotongan persentil, lalu grid_id,
sehingga hasil tidak bergantung pada urutan baris.

Skor adalah INDEKS PRIORITAS relatif terhadap grid lain dalam himpunan yang sama, bukan model
risiko kesehatan dan bukan estimasi kausal.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from . import config as C

NORM_METHODS = ("minmax", "rank")


def norm01(x: pd.Series, clip=C.NORM_CLIP, method: str = "minmax") -> pd.Series:
    """Skala 0-1 dengan arah dipertahankan (nilai besar -> mendekati 1). NaN tetap NaN.

    method="minmax": min-max setelah dipotong pada persentil `clip` (clip=None = min-max murni).
    method="rank":   peringkat persentil (rata-rata untuk seri), dipetakan ke [0, 1].
    Deret konstan menghasilkan 0.5 (tidak membedakan grid).
    """
    x = pd.Series(x, dtype=float)
    v = x.dropna()
    if v.empty:
        return x
    if method == "rank":
        if v.nunique() == 1:
            return pd.Series(0.5, index=x.index).where(x.notna())
        r = x.rank(method="average")
        return (r - 1) / (len(v) - 1)
    if method != "minmax":
        raise ValueError(f"method harus salah satu dari {NORM_METHODS}")
    lo, hi = (v.quantile(clip[0]), v.quantile(clip[1])) if clip else (v.min(), v.max())
    if not hi > lo:
        return pd.Series(0.5, index=x.index).where(x.notna())
    return ((x - lo) / (hi - lo)).clip(0.0, 1.0)


def _park_distance(df: pd.DataFrame) -> pd.Series:
    return df["park_distance_used_m"] if "park_distance_used_m" in df.columns else df["park_distance_m"]


def components(
    df: pd.DataFrame,
    clip=C.NORM_CLIP,
    park_mode: str = "continuous",
    park_cap: float = C.PARK_CAP_M,
    park_thr: float | None = None,
    method: str = "minmax",
) -> pd.DataFrame:
    """Komponen 0-1 untuk baris df (biasanya grid yang layak).

    lst          n(lst_c)                                  LST tinggi -> prioritas tinggi
    ndvi_low     1 - n(ndvi)                               vegetasi rendah -> prioritas tinggi
    pop          n(log1p(population))                      jumlah penduduk terpapar
    pop_density  n(log1p(population / area_km2))           sensitivitas: kepadatan, bukan jumlah
    vuln         n(log1p(pop_child + pop_elderly))         jumlah penduduk usia rentan
    vuln_share   n((pop_child + pop_elderly)/population)   sensitivitas: komposisi usia
    park_deficit min(jarak, cap)/cap  (continuous)         tidak dinormalisasi ulang: 0 m -> 0, >= cap -> 1
                 1[jarak > park_thr]  (binary)
    trees_low    1 - n(trees_prob)                         sensitivitas Dynamic World (bila ada)
    """
    c = pd.DataFrame(index=df.index)
    kw = {"clip": clip, "method": method}
    c["lst"] = norm01(df["lst_c"], **kw)
    c["ndvi_low"] = 1.0 - norm01(df["ndvi"], **kw)
    c["pop"] = norm01(np.log1p(df["population"]), **kw)
    if "pop_density_km2" in df.columns:
        c["pop_density"] = norm01(np.log1p(df["pop_density_km2"]), **kw)
    vul = df["pop_vulnerable"] if "pop_vulnerable" in df.columns else df["pop_child"] + df["pop_elderly"]
    c["vuln"] = norm01(np.log1p(vul), **kw)
    if "vuln_share" in df.columns:
        c["vuln_share"] = norm01(df["vuln_share"], **kw)
    if "trees_prob" in df.columns and df["trees_prob"].notna().any():
        c["trees_low"] = 1.0 - norm01(df["trees_prob"], **kw)
    d = _park_distance(df)
    if park_mode == "continuous":
        if not park_cap > 0:
            raise ValueError("park_cap harus > 0")
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
    if np.isnan(s).any():
        raise ValueError("rank_desc: skor memuat NaN; peringkat hanya untuk grid layak.")
    k = np.asarray(tiebreak, dtype=str)
    sec = np.zeros(len(s)) if secondary is None else np.nan_to_num(np.asarray(secondary, dtype=float), nan=-np.inf)
    order = np.lexsort((k, -sec, -s))
    r = np.empty(len(s), dtype=int)
    r[order] = np.arange(1, len(s) + 1)
    return pd.Series(r, index=score.index)


def score_rank(v: pd.DataFrame, weights: dict[str, float], clip=C.NORM_CLIP, method: str = "minmax", **comp_kw):
    """Skor dan peringkat untuk grid layak v.

    Pemotongan persentil (clip) membuat banyak grid di ekor atas bernilai sama (=1). Agar peringkat
    tidak ditentukan oleh grid_id, seri dipecah dahulu oleh skor tanpa pemotongan (min-max murni).
    """
    s = weighted_score(components(v, clip=clip, method=method, **comp_kw), weights)
    if s.isna().any():
        raise ValueError(f"{int(s.isna().sum())} grid layak punya komponen kosong; periksa kelayakan data.")
    raw = weighted_score(components(v, clip=None, **comp_kw), weights) if (clip and method == "minmax") else s
    return s, rank_desc(s, v[C.KEY], secondary=raw)


def n_top(n_valid: int, frac: float = C.TOP_FRAC) -> int:
    if not 0 < frac <= 1:
        raise ValueError("frac harus di (0, 1]")
    return int(math.ceil(frac * n_valid)) if n_valid > 0 else 0


def top_mask(rank: pd.Series, n_valid: int, frac: float = C.TOP_FRAC) -> pd.Series:
    return (rank <= n_top(n_valid, frac)).fillna(False).astype(bool)


def priority_class(rank: pd.Series, n_valid: int, cutoffs=C.CLASS_CUTOFFS, labels=C.CLASS_LABELS) -> pd.Series:
    """Kelas prioritas dari peringkat: batas kumulatif ceil(cutoff * n_valid). NaN untuk grid tidak layak."""
    if len(labels) != len(cutoffs) + 1:
        raise ValueError("labels harus satu lebih banyak dari cutoffs")
    bounds = [n_top(n_valid, f) for f in cutoffs]
    r = pd.to_numeric(rank, errors="coerce")
    out = pd.Series(pd.NA, index=rank.index, dtype="object")
    prev = 0
    for b, lab in zip([*bounds, n_valid], labels):
        out[(r > prev) & (r <= b)] = lab
        prev = b
    return out


def build_priority_table(
    df: pd.DataFrame,
    models: dict[str, dict[str, float]] = C.MODELS,
    top_frac: float = C.TOP_FRAC,
    clip=C.NORM_CLIP,
    park_cap: float = C.PARK_CAP_M,
    method: str = "minmax",
) -> pd.DataFrame:
    """Skor, peringkat, kelas, dan penanda top-N semua model pada SATU himpunan grid valid yang sama.

    df: keluaran data.clean_values (harus punya kolom `valid`). Normalisasi dihitung pada himpunan valid,
    sehingga skor antar-model sebanding dan tidak ada pencampuran populasi grid yang berbeda.
    """
    if "valid" not in df.columns:
        raise ValueError("df harus berasal dari data.clean_values (kolom 'valid').")
    v = df.loc[df["valid"]]
    if v.empty:
        raise ValueError("Tidak ada grid valid; periksa tabel kualitas data (remote sensing sudah ada?).")
    out = pd.DataFrame({C.KEY: df[C.KEY].to_numpy()}, index=df.index)
    out["valid"] = df["valid"].to_numpy()
    comp = components(v, clip=clip, park_cap=park_cap, method=method)
    for name in ("lst", "ndvi_low", "pop", "vuln", "park_deficit"):
        col = "c_park" if name == "park_deficit" else f"c_{name}"
        out[col] = comp[name].reindex(df.index)
    nv = len(v)
    for m, w in models.items():
        k = m.lower()
        s, r = score_rank(v, w, clip=clip, park_cap=park_cap, method=method)
        out[f"{k}_score"] = s.reindex(df.index)
        out[f"{k}_rank"] = r.reindex(df.index).astype("Int64")
        out[f"{k}_top"] = top_mask(out[f"{k}_rank"], nv, top_frac)
        out[f"{k}_class"] = priority_class(out[f"{k}_rank"], nv)
    return out.reset_index(drop=True)


def component_correlations(df: pd.DataFrame, method: str = "spearman") -> pd.DataFrame:
    """Korelasi antar-komponen pada grid layak (diagnostik redundansi / double counting).

    Komponen yang hanya butuh data Person 2 (pop, vuln, park_deficit, ...) dapat dihitung
    walaupun remote sensing belum tersedia.
    """
    cols = ["population", "pop_child", "pop_elderly"]
    p2 = df.loc[df[cols].notna().all(axis=1) & _park_distance(df).notna()]
    comp = components(p2)
    keep = [c for c in comp.columns if comp[c].notna().any()]
    return comp[keep].corr(method=method)
