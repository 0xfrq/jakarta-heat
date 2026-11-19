"""Autokorelasi spasial (Moran global dan lokal/LISA). Memakai libpysal dan esda.

Baseline bobot: Queen contiguity pada poligon grid 500 m, distandardisasi baris (row-standardized).
Alasan: grid reguler -> Queen memberi hingga 8 tetangga langsung (termasuk diagonal) yang simetris dan
mudah dijelaskan; Rook (4 tetangga) dan KNN-8 dipakai sebagai uji sensitivitas.

Grid tanpa tetangga (islands) dikeluarkan dari uji dan DILAPORKAN, lalu bobot dibangun ulang sehingga
standardisasi baris terdefinisi untuk semua grid yang diuji.

Bagian murni (bh_fdr, lisa_labels, lattice_neighbors) tidak butuh paket spasial.
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

from . import config as C

QUAD = {1: "HH", 2: "LH", 3: "LL", 4: "HL"}  # skema PySAL
LISA_LABELS = {"HH": "Tinggi-Tinggi", "LL": "Rendah-Rendah", "HL": "Tinggi-Rendah (outlier)",
               "LH": "Rendah-Tinggi (outlier)", "ns": "Tidak signifikan"}
_ID_RE = re.compile(r"R(\d+)_C(\d+)$")


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


def parse_rc(grid_id: str) -> tuple[int, int]:
    m = _ID_RE.search(str(grid_id))
    if not m:
        raise ValueError(f"grid_id tidak berpola ..R<baris>_C<kolom>: {grid_id}")
    return int(m.group(1)), int(m.group(2))


def lattice_neighbors(ids, kind: str = "queen") -> dict[int, list[int]]:
    """Tetangga dari indeks baris/kolom grid_id (posisi 0..n-1). Independen dari geometri terpotong."""
    rc = [parse_rc(i) for i in ids]
    pos = {v: i for i, v in enumerate(rc)}
    if kind == "queen":
        offs = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0)]
    elif kind == "rook":
        offs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    else:
        raise ValueError("kind harus 'queen' atau 'rook'")
    return {i: sorted(pos[(r + dr, c + dc)] for dr, dc in offs if (r + dr, c + dc) in pos)
            for i, (r, c) in enumerate(rc)}


def _need():
    try:
        import esda  # noqa: F401
        import libpysal  # noqa: F401
    except ImportError as exc:
        raise ImportError("Pasang dulu: python -m pip install libpysal esda") from exc


def queen_neighbors_fast(gdf) -> dict[int, list[int]]:
    """Queen contiguity via STRtree 'intersects' (berbagi titik atau sisi) untuk poligon yang tidak tumpang tindih.

    Hasilnya diuji identik dengan libpysal Queen pada master grid (20.988 pasangan), tetapi ~1000x lebih cepat.
    """
    import shapely

    geoms = gdf.geometry.values
    a, b = shapely.STRtree(geoms).query(geoms, predicate="intersects")
    keep = a != b
    nb: dict[int, list[int]] = {i: [] for i in range(len(geoms))}
    for i, j in zip(a[keep], b[keep]):
        nb[int(i)].append(int(j))
    return {i: sorted(v) for i, v in nb.items()}


def build_weights(gdf, kind: str = "queen"):
    """Bobot spasial berdasarkan urutan baris gdf (posisi 0..n-1). gdf harus sudah reset_index."""
    _need()
    from libpysal import weights as W

    if kind == "queen":
        return W.W(queen_neighbors_fast(gdf), silence_warnings=True)
    if kind in ("queen_libpysal", "rook"):
        cls = W.Queen if kind == "queen_libpysal" else W.Rook
        try:
            return cls.from_dataframe(gdf, use_index=False, silence_warnings=True)
        except TypeError:  # libpysal lama
            return cls.from_dataframe(gdf)
    if kind == "knn8":
        pts = gdf.to_crs(C.CRS_PROJECTED).geometry.centroid
        xy = np.column_stack([pts.x.to_numpy(), pts.y.to_numpy()])
        return W.KNN.from_array(xy, k=8, silence_warnings=True)
    if kind in ("lattice_queen", "lattice_rook"):
        nb = lattice_neighbors(gdf[C.KEY], kind.split("_")[1])
        return W.W(nb, silence_warnings=True)
    raise ValueError(f"kind tidak dikenal: {kind}")


def queen_weights(gdf):
    """Kompatibilitas nama lama."""
    return build_weights(gdf, "queen")


def prepare_weights(gdf, kind: str = "queen"):
    """Bangun bobot, keluarkan islands, bangun ulang, standardisasi baris.

    Kembalikan (w, gdf_dipakai, daftar grid_id islands yang dikeluarkan).
    """
    sub = gdf.reset_index(drop=True)
    dropped: list[str] = []
    for _ in range(5):
        w = build_weights(sub, kind)
        if not w.islands:
            break
        dropped += list(sub.loc[list(w.islands), C.KEY])
        sub = sub.drop(index=list(w.islands)).reset_index(drop=True)
    else:
        raise RuntimeError("Islands masih ada setelah 5 iterasi.")
    w.transform = "r"
    return w, sub, dropped


def global_moran(y, w, permutations: int = C.PERMUTATIONS, seed: int = C.SEED) -> dict:
    _need()
    from esda.moran import Moran

    y = np.asarray(y, dtype=float)
    if np.isnan(y).any():
        raise ValueError("global_moran: y memuat NaN; saring grid terlebih dahulu.")
    np.random.seed(seed)  # Moran memakai RNG global; ini membuat p_sim dapat diulang
    mi = Moran(y, w, permutations=permutations, two_tailed=False)
    # Explicit upper tail for the predeclared positive-autocorrelation hypothesis.
    positive_p = (1 + int(np.count_nonzero(mi.sim >= mi.I))) / (permutations + 1)
    return {
        "I": float(mi.I),
        "EI": float(mi.EI),
        "z_sim": float(mi.z_sim),
        "p_sim": float(positive_p),
        "alternative": "greater",
        "p_norm": float(mi.p_norm),
        "n": int(len(y)),
        "permutations": int(permutations),
        "seed": int(seed),
        "n_islands": int(len(w.islands)),
        "mean_neighbors": float(w.mean_neighbors),
    }


def local_moran(y, w, permutations: int = C.PERMUTATIONS, seed: int = C.SEED, alpha: float = C.LISA_ALPHA,
                alternative: str = "directed") -> pd.DataFrame:
    """LISA dengan p_sim berbasis permutasi bersyarat; klaster dilaporkan dua kali: p<alpha dan FDR-BH."""
    _need()
    from esda.moran import Moran_Local

    y = np.asarray(y, dtype=float)
    if np.isnan(y).any():
        raise ValueError("local_moran: y memuat NaN; saring grid terlebih dahulu.")
    if alternative not in ("directed", "two-sided"):
        raise ValueError("alternative must be directed or two-sided")
    lm = Moran_Local(y, w, permutations=permutations, seed=seed, alternative=alternative)
    p = np.asarray(lm.p_sim, dtype=float)
    rej = bh_fdr(p, alpha)
    return pd.DataFrame(
        {
            "lisa_I": np.asarray(lm.Is, dtype=float),
            "p_sim": p,
            "kuadran": [QUAD.get(int(a), "ns") for a in lm.q],
            "klaster_p05": lisa_labels(lm.q, p, alpha),
            "klaster_fdr": lisa_labels(lm.q, p, alpha, reject=rej),
            "klaster_by": lisa_labels(lm.q, p, alpha, reject=bh_fdr(p, alpha / np.sum(1 / np.arange(1, len(p) + 1)))),
            "alternative": alternative,
            "permutations": permutations,
            "seed": seed,
            "testing_family": "one preselected variable-map; all non-island eligible grids",
        }
    )


def moran_table(gdf, columns, kinds=("queen",), permutations: int = C.PERMUTATIONS, seed: int = C.SEED) -> pd.DataFrame:
    """Moran global untuk beberapa variabel x beberapa definisi tetangga.

    Tiap variabel memakai grid dengan nilai tidak kosong saja; jumlah grid dan islands dilaporkan.
    """
    rows = []
    for col in columns:
        sub = gdf.loc[gdf[col].notna()].reset_index(drop=True)
        if len(sub) < 10:
            continue
        for kind in kinds:
            w, used, dropped = prepare_weights(sub, kind)
            r = global_moran(used[col], w, permutations, seed)
            rows.append({"variabel": col, "bobot": kind, "n_islands_dikeluarkan": len(dropped), **r})
    return pd.DataFrame(rows)


def lisa_for(gdf, col: str, kind: str = "queen", permutations: int = C.PERMUTATIONS, seed: int = C.SEED,
             alpha: float = C.LISA_ALPHA, alternative: str = "directed") -> tuple[pd.DataFrame, list[str]]:
    """LISA untuk satu variabel; keluaran berkunci grid_id. Islands dikembalikan terpisah."""
    sub = gdf.loc[gdf[col].notna()].reset_index(drop=True)
    w, used, dropped = prepare_weights(sub, kind)
    out = local_moran(used[col], w, permutations, seed, alpha, alternative)
    out.insert(0, C.KEY, used[C.KEY].to_numpy())
    out.insert(1, "variabel", col)
    out.insert(2, "bobot", kind)
    return out, dropped
