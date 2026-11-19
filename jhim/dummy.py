"""Data dummy sintetis untuk melatih Job 6A-6C sebelum data asli Orang 1 dan 2 tiba.

Bidang halus (spasial berautokorelasi) + derau, sehingga Moran's I bukan nol.
Semua berkas dummy memuat kolom is_dummy=1 supaya tidak mungkin dikira data asli.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C


def _field(x, y, rng, n_bumps=6):
    f = np.zeros_like(x)
    for _ in range(n_bumps):
        cx, cy = rng.uniform(0, 1, 2)
        s = rng.uniform(0.12, 0.3)
        f += rng.uniform(0.5, 1.0) * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * s * s))
    return (f - f.min()) / (np.ptp(f) or 1.0)


def make_dummy_inputs(grid: pd.DataFrame, seed: int = C.SEED):
    """grid: kolom grid_id, x, y (meter). Kembalikan (remote_sensing_df, population_accessibility_df)."""
    rng = np.random.default_rng(seed)
    n = len(grid)
    x = (grid["x"] - grid["x"].min()) / (np.ptp(grid["x"]) or 1.0)
    y = (grid["y"] - grid["y"].min()) / (np.ptp(grid["y"]) or 1.0)
    x, y = x.to_numpy(), y.to_numpy()
    heat, dens, green = _field(x, y, rng), _field(x, y, rng), _field(x, y, rng)

    lst = 29.0 + 7.0 * (0.6 * heat + 0.4 * dens) + rng.normal(0, 0.8, n)
    ndvi = np.clip(0.55 - 0.4 * (0.6 * heat + 0.4 * dens) + 0.2 * green + rng.normal(0, 0.05, n), -0.1, 0.9)
    population = np.round(np.exp(5.0 + 3.0 * dens + rng.normal(0, 0.4, n)))
    child = np.round(population * rng.uniform(0.15, 0.27, n))
    elder = np.round(population * rng.uniform(0.03, 0.10, n))
    dist = np.clip(60 + 1900 * (1 - green) ** 2 + rng.normal(0, 80, n), 0, None)

    rs = pd.DataFrame({C.KEY: grid[C.KEY].to_numpy(), "lst_c": lst.round(2), "ndvi": ndvi.round(3), "is_dummy": 1})
    pop = pd.DataFrame(
        {
            C.KEY: grid[C.KEY].to_numpy(),
            "population": population,
            "pop_child": child,
            "pop_elderly": elder,
            "park_distance_m": dist.round(0),
            "park_access_500m": (dist <= 500).astype(float),
            "is_dummy": 1,
        }
    )
    # kekurangan data realistis: awan (LST kosong), taman tak terjangkau, baris hilang
    rs.loc[rng.random(n) < 0.02, "lst_c"] = np.nan
    unreach = rng.random(n) < 0.01
    pop.loc[unreach, ["park_distance_m", "park_access_500m"]] = np.nan
    pop = pop.loc[rng.random(n) >= 0.005].reset_index(drop=True)
    return rs, pop
