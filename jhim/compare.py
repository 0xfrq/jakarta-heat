"""Perbandingan antar-model (Job 6B, bagian tanpa data spasial)."""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd

from . import config as C


def model_keys(pri: pd.DataFrame) -> list[str]:
    return sorted({c.split("_")[0] for c in pri.columns if c.endswith("_score")})


def spearman_matrix(pri: pd.DataFrame, keys=None) -> pd.DataFrame:
    keys = keys or model_keys(pri)
    v = pri.loc[pri["valid"]]
    m = v[[f"{k}_score" for k in keys]].astype(float).corr(method="spearman")
    m.index = m.columns = [k.upper() for k in keys]
    return m


def jaccard_matrix(pri: pd.DataFrame, keys=None) -> pd.DataFrame:
    keys = keys or model_keys(pri)
    tops = {k: set(pri.loc[pri[f"{k}_top"], C.KEY]) for k in keys}
    m = pd.DataFrame(index=[k.upper() for k in keys], columns=[k.upper() for k in keys], dtype=float)
    for a, b in itertools.product(keys, keys):
        u = len(tops[a] | tops[b])
        m.loc[a.upper(), b.upper()] = len(tops[a] & tops[b]) / u if u else np.nan
    return m


def pairwise_long(pri: pd.DataFrame, keys=None) -> pd.DataFrame:
    """Tabel panjang untuk model_comparison.csv: metrik, model_a, model_b, nilai."""
    keys = keys or model_keys(pri)
    sp, ja = spearman_matrix(pri, keys), jaccard_matrix(pri, keys)
    rows = []
    for a, b in itertools.combinations([k.upper() for k in keys], 2):
        rows.append({"metrik": "spearman_skor", "model_a": a, "model_b": b, "nilai": float(sp.loc[a, b])})
        rows.append({"metrik": "jaccard_top", "model_a": a, "model_b": b, "nilai": float(ja.loc[a, b])})
    return pd.DataFrame(rows)


def top_coverage(pri: pd.DataFrame, feat: pd.DataFrame, keys=None) -> pd.DataFrame:
    """Siapa dan apa yang ada di 10% grid teratas tiap model (dibanding semua grid valid)."""
    keys = keys or model_keys(pri)
    cols = [C.KEY, "population", "pop_child", "pop_elderly", "lst_c", "ndvi", "park_distance_m"]
    j = pri[[C.KEY, "valid", *[f"{k}_top" for k in keys]]].merge(feat[cols], on=C.KEY, how="left", validate="one_to_one")
    j = j.loc[j["valid"]].copy()
    j["vulnerable"] = j["pop_child"] + j["pop_elderly"]
    tot_pop, tot_vul = float(j["population"].sum()), float(j["vulnerable"].sum())

    def row(label, sub):
        return {
            "kelompok": label,
            "n_grid": int(len(sub)),
            "populasi": float(sub["population"].sum()),
            "pct_populasi_valid": 100 * float(sub["population"].sum()) / tot_pop if tot_pop else np.nan,
            "penduduk_rentan": float(sub["vulnerable"].sum()),
            "pct_rentan_valid": 100 * float(sub["vulnerable"].sum()) / tot_vul if tot_vul else np.nan,
            "lst_rata2": float(sub["lst_c"].mean()),
            "ndvi_rata2": float(sub["ndvi"].mean()),
            "jarak_taman_median_m": float(sub["park_distance_m"].median()),
            "pct_grid_taman_lebih_500m": 100 * float((sub["park_distance_m"] > 500).mean()),
        }

    rows = [row(f"{k.upper()} top", j.loc[j[f"{k}_top"]]) for k in keys]
    rows.append(row("Semua grid valid", j))
    return pd.DataFrame(rows)


def rank_shift(pri: pd.DataFrame, a: str = "m1", b: str = "m4") -> pd.DataFrame:
    """Perubahan peringkat grid dari model a ke model b.

    shift = rank_a - rank_b; POSITIF berarti grid naik prioritas di model b (angka peringkat mengecil).
    """
    v = pri.loc[pri["valid"], [C.KEY, f"{a}_rank", f"{b}_rank", f"{a}_top", f"{b}_top"]].copy()
    v = v.rename(columns={f"{a}_rank": "rank_a", f"{b}_rank": "rank_b", f"{a}_top": "top_a", f"{b}_top": "top_b"})
    v["shift"] = (v["rank_a"] - v["rank_b"]).astype(int)

    def trans(r):
        if r.top_a and r.top_b:
            return "tetap top"
        if r.top_b:
            return f"masuk top di {b.upper()}"
        if r.top_a:
            return f"keluar top di {b.upper()}"
        return "bukan top"

    v["transisi"] = v.apply(trans, axis=1)
    return v.sort_values("shift", ascending=False, kind="stable").reset_index(drop=True)


def retop(pri: pd.DataFrame, frac: float = C.TOP_FRAC) -> pd.DataFrame:
    """Hitung ulang kolom *_top dari peringkat untuk bagian teratas `frac` (dipakai slider dashboard)."""
    from .models import n_top

    out = pri.copy()
    nv = int(out["valid"].sum())
    for k in model_keys(out):
        out[f"{k}_top"] = (out[f"{k}_rank"] <= n_top(nv, frac)).fillna(False).astype(bool)
    return out
