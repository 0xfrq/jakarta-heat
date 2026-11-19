"""Autokorelasi spasial (Moran global dan lokal/LISA). Memakai libpysal dan esda.

Bagian murni (bh_fdr, lisa_labels) tidak butuh paket spasial dan diuji terpisah.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C

QUAD = {1: "HH", 2: "LH", 3: "LL", 4: "HL"}  # skema PySAL (geoda_quads=False)


def bh_fdr(p, q: float = 0.05) -> np.ndarray:
    """Benjamini-Hochberg: True untuk hipotesis yang ditolak pada FDR q."""
    p = np.asarray(p, dtype=float)
    ok = np.isfinite(p)
    rej = np.zeros(len(p), dtype=bool)
    pv = p[ok]
    m = len(pv)
    if m == 0:
        return rej
    order = np.argsort(pv, kind="stable")
    passed = pv[order] <= q * (np.arange(1, m + 1) / m)
    if passed.any():
        k = np.max(np.nonzero(passed)[0])
        sel = np.zeros(m, dtype=bool)
        sel[order[: k + 1]] = True
        rej[np.nonzero(ok)[0]] = sel
    return rej


def lisa_labels(q, p, alpha: float = C.LISA_ALPHA, reject=None) -> list[str]:
    """Label klaster: HH/LH/LL/HL bila signifikan, selain itu 'ns'. reject (bool) menggantikan p<alpha."""
    q = np.asarray(q)
    sig = np.asarray(reject, dtype=bool) if reject is not None else (np.asarray(p, dtype=float) < alpha)
    return [QUAD.get(int(a), "ns") if s else "ns" for a, s in zip(q, sig)]


def _need():
    try:
        import esda  # noqa: F401
        import libpysal  # noqa: F401
    except ImportError as exc:
        raise ImportError("Pasang dulu: python -m pip install libpysal esda") from exc


def queen_weights(gdf):
    """Bobot Queen berdasarkan urutan baris gdf (posisi 0..n-1). gdf harus sudah reset_index."""
    _need()
    from libpysal.weights import Queen

    try:
        w = Queen.from_dataframe(gdf, use_index=False)
    except TypeError:  # versi libpysal lama tanpa use_index
        w = Queen.from_dataframe(gdf)
    return w


def global_moran(y, w, permutations: int = C.PERMUTATIONS, seed: int = C.SEED) -> dict:
    _need()
    from esda.moran import Moran

    np.random.seed(seed)  # Moran memakai RNG global; ini membuat p_sim dapat diulang
    mi = Moran(np.asarray(y, dtype=float), w, permutations=permutations)
    return {
        "I": float(mi.I),
        "EI": float(mi.EI),
        "z_sim": float(mi.z_sim),
        "p_sim": float(mi.p_sim),
        "p_norm": float(mi.p_norm),
        "n": int(len(y)),
        "permutations": int(permutations),
        "n_islands": int(len(w.islands)),
    }


def local_moran(y, w, permutations: int = C.PERMUTATIONS, seed: int = C.SEED, alpha: float = C.LISA_ALPHA) -> pd.DataFrame:
    _need()
    from esda.moran import Moran_Local

    lm = Moran_Local(np.asarray(y, dtype=float), w, permutations=permutations, seed=seed)
    p = np.asarray(lm.p_sim, dtype=float)
    rej = bh_fdr(p, alpha)
    return pd.DataFrame(
        {
            "lisa_I": np.asarray(lm.Is, dtype=float),
            "p_sim": p,
            "kuadran": [QUAD.get(int(a), "ns") for a in lm.q],
            "klaster_p05": lisa_labels(lm.q, p, alpha),
            "klaster_fdr": lisa_labels(lm.q, p, alpha, reject=rej),
        }
    )
