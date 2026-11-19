"""Fixture uji Agent 3. Semua data di sini SINTETIS (test fixtures) dan hanya ditulis ke tmp_path."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from jhim import config as C  # noqa: E402

NR, NC = 8, 10  # 80 sel
X0, Y0, S = 690000.0, 9300000.0, 500.0


def grid_ids(nr=NR, nc=NC):
    return [f"JKT_R{r:03d}_C{c:03d}" for r in range(nr) for c in range(nc)]


def make_grid_gdf(nr=NR, nc=NC, crs=C.CRS_PROJECTED, isolated: bool = False):
    import geopandas as gpd
    from shapely.geometry import box

    rows = []
    for r in range(nr):
        for c in range(nc):
            rows.append({C.KEY: f"JKT_R{r:03d}_C{c:03d}", "kota": "Kota A" if c < nc // 2 else "Kota B",
                         "area_km2": 0.25, "coverage_ratio": 1.0,
                         "geometry": box(X0 + c * S, Y0 + r * S, X0 + (c + 1) * S, Y0 + (r + 1) * S)})
    if isolated:  # sel jauh tanpa tetangga
        rows.append({C.KEY: "JKT_R050_C050", "kota": "Kota B", "area_km2": 0.25, "coverage_ratio": 1.0,
                     "geometry": box(X0 + 50 * S, Y0 + 50 * S, X0 + 51 * S, Y0 + 51 * S)})
    return gpd.GeoDataFrame(rows, geometry="geometry", crs=crs)


def p2_frame(ids, seed=1):
    rng = np.random.default_rng(seed)
    n = len(ids)
    pop = rng.uniform(100, 8000, n)
    pop[3] = 0.0  # populasi nol
    child = np.round(pop * 0.22, 3)
    elder = np.round(pop * 0.07, 3)
    dist = rng.uniform(0, 2500, n)
    dist[5] = 0.0  # jarak nol yang SAH (grid berisi/menempel taman)
    dist[[7, 11, 13]] = np.nan  # rute tidak dihitung
    snap = rng.uniform(5, 100, n)
    snap[[2, 9]] = [300.0, 420.0]
    reach = np.where(np.isnan(dist), 0, 1)
    a500 = np.where(np.isnan(dist), 0, (dist <= 500).astype(int))
    a1000 = np.where(np.isnan(dist), 0, (dist <= 1000).astype(int))
    return pd.DataFrame({C.KEY: ids, "population": pop, "pop_child": child, "pop_elderly": elder,
                         "park_distance_m": dist, "grid_snap_m": snap, "park_reachable": reach,
                         "park_access_500m": a500, "park_access_1000m": a1000})


def rs_frame(ids, seed=2):
    rng = np.random.default_rng(seed)
    rc = np.array([[int(i[5:8]), int(i[10:13])] for i in ids], dtype=float)
    lst = 33 + 0.8 * rc[:, 1] + rng.normal(0, 0.3, len(ids))  # gradien barat-timur (autokorelasi positif)
    ndvi = np.clip(0.6 - 0.04 * rc[:, 1] + rng.normal(0, 0.02, len(ids)), -0.2, 0.9)
    return pd.DataFrame({C.KEY: ids, "lst_c": lst.round(3), "ndvi": ndvi.round(4),
                         "lst_valid_frac": 1.0, "trees_prob": np.clip(ndvi, 0, 1)})


def write_root(root: Path, with_rs: bool = True, rs: pd.DataFrame | None = None, p2: pd.DataFrame | None = None,
               isolated: bool = False) -> C.Paths:
    proc = root / "data/processed"
    proc.mkdir(parents=True, exist_ok=True)
    g = make_grid_gdf(isolated=isolated)
    g.to_file(proc / "grid_500m_jakarta.gpkg", layer="grid_500m_jakarta", driver="GPKG")
    ids = g[C.KEY].tolist()
    g.drop(columns="geometry").to_csv(proc / "grid_master.csv", index=False)
    (p2 if p2 is not None else p2_frame(ids)).to_csv(proc / "spatial_features.csv", index=False)
    if with_rs:
        (rs if rs is not None else rs_frame(ids)).to_csv(proc / "remote_sensing_grid.csv", index=False)
    return C.Paths(root=root)


@pytest.fixture(autouse=True)
def _no_env(monkeypatch):
    for k in ("JHIM_INPUT_DIR", "JHIM_RS_PATH", "JHIM_DEMOGRAPHIC_SUPPORT", "JHIM_DEMOGRAPHIC_CORRECTED"):
        monkeypatch.delenv(k, raising=False)


@pytest.fixture
def root_full(tmp_path):
    return write_root(tmp_path, with_rs=True)


@pytest.fixture
def root_p2(tmp_path):
    return write_root(tmp_path, with_rs=False)


@pytest.fixture
def feat_full(root_full):
    from jhim import data as D

    feat, _, _ = D.load_features(root_full)
    return feat
