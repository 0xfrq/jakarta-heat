"""Uji sensitivitas prioritas (Job 6B). Semua skenario memakai set grid valid yang sama."""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C
from .models import n_top, normalize_weights, score_rank


def _scenarios(v: pd.DataFrame, weights: dict[str, float]):
    """Hasilkan daftar (nama, kelompok, skor, peringkat) untuk tiap skenario."""
    out = []

    def add(name, group, w, **kw):
        s, r = score_rank(v, w, **kw)
        out.append((name, group, s, r))

    if len(weights) > 1:
        for comp_name in weights:
            for f in C.WEIGHT_FACTORS:
                w = dict(weights)
                w[comp_name] = w[comp_name] * f
                add(f"bobot {comp_name} x{f:g}", "bobot", w)
    if "park_deficit" in weights:
        for thr in C.PARK_THRESHOLDS_M:
            add(f"akses taman biner >{thr:g} m", "ambang taman", weights, park_mode="binary", park_thr=thr)
    add("normalisasi min-max murni", "normalisasi", weights, clip=None)
    add("normalisasi persentil 1-99", "normalisasi", weights, clip=(0.01, 0.99))
    return out


def run_sensitivity(feat: pd.DataFrame, model: str = "M4", top_frac: float = C.TOP_FRAC, weights=None):
    """Bandingkan top-N baseline dengan tiap skenario.

    feat: keluaran data.clean_values (kolom `valid` dipakai).
    Kembalikan (ringkasan per skenario, stabilitas per grid, info dict).
    """
    w0 = normalize_weights(weights or C.MODELS[model])
    v = feat.loc[feat["valid"]].copy()
    if v.empty:
        raise ValueError("Tidak ada grid valid.")
    nt = n_top(len(v), top_frac)
    scen = _scenarios(v, w0)
    base_score, base_rank = score_rank(v, w0)
    base_top = set(v.loc[base_rank <= nt, C.KEY])

    rows, in_top = [], {}
    for name, group, s, r in scen:
        top = set(v.loc[r <= nt, C.KEY])
        u = len(top | base_top)
        rows.append(
            {
                "skenario": name,
                "kelompok": group,
                "jaccard_vs_baseline": len(top & base_top) / u if u else np.nan,
                "spearman_vs_baseline": float(pd.Series(s.to_numpy()).corr(pd.Series(base_score.to_numpy()), method="spearman")),
                "grid_top_berubah": int(len(base_top - top)),
            }
        )
        in_top[name] = v[C.KEY].isin(top).to_numpy()
    summ = pd.DataFrame(rows)

    M = np.vstack(list(in_top.values())) if in_top else np.zeros((0, len(v)), dtype=bool)
    share = M.mean(axis=0) if len(M) else np.full(len(v), np.nan)
    stab = pd.DataFrame(
        {
            C.KEY: v[C.KEY].to_numpy(),
            "baseline_top": v[C.KEY].isin(base_top).to_numpy(),
            "stable_share": share,
            "in_all_scenarios": M.all(axis=0) if len(M) else False,
        }
    )
    bt = stab.loc[stab["baseline_top"]]
    info = {
        "model": model,
        "n_valid": int(len(v)),
        "n_top": int(nt),
        "n_scenarios": int(len(scen)),
        "n_baseline_top_stable": int((bt["stable_share"] >= C.STABLE_SHARE).sum()),
        "share_baseline_top_stable": float((bt["stable_share"] >= C.STABLE_SHARE).mean()) if len(bt) else float("nan"),
        "n_baseline_top_in_all": int(bt["in_all_scenarios"].sum()),
        "min_jaccard": float(summ["jaccard_vs_baseline"].min()) if len(summ) else float("nan"),
        "stable_threshold": C.STABLE_SHARE,
    }
    return summ, stab, info
