"""Person 1 / Agent 1 -- validate data/processed/remote_sensing_grid.csv and its source rasters.

Checks the data contract with the master grid, value ranges/units, missing-value semantics,
raster nodata semantics, and recomputes grid means independently (analytic pixel/cell
overlap, no exactextract) for a sample of full interior cells.

Writes:
* data/processed/remote_sensing_qa_problem_grids.csv  -- grids with any QA flag
* outputs/qa/remote_sensing_qa.json                    -- machine-readable QA report
* outputs/maps/remote_sensing_grid_preview.png         -- grid-level maps for visual QA

Exit code 1 if any CRITICAL check fails.

    python scripts/02d_validate_remote_sensing.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
RS_CSV = PROC / "remote_sensing_grid.csv"
GRID_CSV = PROC / "grid_master.csv"
GRID_GPKG = PROC / "grid_500m_jakarta.gpkg"
SPATIAL = PROC / "spatial_features.csv"
LANDSAT_TIF = PROC / "remote_sensing" / "jakarta_2024_lst_ndvi_qa.tif"
DW_PROB_TIF = PROC / "remote_sensing" / "jakarta_2024_trees_built_probability.tif"
PROBLEMS = PROC / "remote_sensing_qa_problem_grids.csv"
QA_JSON = ROOT / "outputs" / "qa" / "remote_sensing_qa.json"
PREVIEW = ROOT / "outputs" / "maps" / "remote_sensing_grid_preview.png"
KEY = "grid_id"

FRACTION_COLS = ["tree_fraction", "grass_fraction", "built_fraction", "lst_valid_fraction",
                 "ndvi_valid_fraction", "landsat_footprint_fraction", "dw_valid_fraction",
                 "water_fraction", "flooded_vegetation_fraction", "crops_fraction", "shrub_fraction",
                 "bare_fraction", "dw_label_valid_fraction", "tree_prob_mean", "built_prob_mean"]

results: list[dict] = []


def check(name: str, ok: bool, detail="", critical=True):
    results.append({"check": name, "ok": bool(ok), "critical": critical, "detail": str(detail)})
    tag = "PASS" if ok else ("FAIL" if critical else "WARN")
    print(f"[{tag}] {name}: {detail}")


def window_mean(src, band: int, bounds) -> float:
    """Exact area-weighted mean of a band over an axis-aligned rectangle (independent of exactextract)."""
    minx, miny, maxx, maxy = bounds
    t = src.transform
    c0 = int(np.floor((minx - t.c) / t.a)); c1 = int(np.ceil((maxx - t.c) / t.a))
    r0 = int(np.floor((maxy - t.f) / t.e)); r1 = int(np.ceil((miny - t.f) / t.e))
    a = src.read(band, window=((r0, r1), (c0, c1))).astype("float64")
    xs = t.c + t.a * np.arange(c0, c1 + 1)
    ys = t.f + t.e * np.arange(r0, r1 + 1)
    wx = np.clip(np.minimum(xs[1:], maxx) - np.maximum(xs[:-1], minx), 0, None)
    wy = np.clip(np.minimum(ys[:-1], maxy) - np.maximum(ys[1:], miny), 0, None)
    w = np.outer(wy, wx)
    ok = np.isfinite(a) & (a != src.nodata)
    return float((a * w)[ok].sum() / w[ok].sum())


def main() -> int:
    rs = pd.read_csv(RS_CSV, dtype={KEY: "string"})
    master = pd.read_csv(GRID_CSV, dtype={KEY: "string"})

    # ---------------- contract
    check("row count equals master grid", len(rs) == len(master), f"{len(rs)} vs {len(master)}")
    check("no duplicated grid_id", not rs[KEY].duplicated().any(), int(rs[KEY].duplicated().sum()))
    check("no missing grid_id", not rs[KEY].isna().any())
    check("grid_id set equals master", set(rs[KEY]) == set(master[KEY]),
          f"missing={len(set(master[KEY]) - set(rs[KEY]))}, extra={len(set(rs[KEY]) - set(master[KEY]))}")
    for c in ["lst_mean_c", "ndvi_mean", "tree_fraction", "grass_fraction", "built_fraction",
              "lst_valid_fraction", "lst_observation_count", "lst_c", "ndvi"]:
        check(f"column present: {c}", c in rs.columns)

    if SPATIAL.exists():
        sp = pd.read_csv(SPATIAL, dtype={KEY: "string"})
        j = sp.merge(rs, on=KEY, how="left", validate="one_to_one", indicator=True)
        check("one-to-one join with spatial_features.csv", len(j) == len(sp) and (j["_merge"] == "both").all(),
              f"{len(j)} rows, unmatched={int((j['_merge'] != 'both').sum())}")

    # ---------------- ranges / units
    lst = rs["lst_mean_c"]
    check("LST in plausible Celsius range [15, 60] (not Kelvin, not DN)", lst.dropna().between(15, 60).all(),
          f"min={lst.min():.2f}, max={lst.max():.2f}")
    check("LST not double-scaled (median between 25 and 50 C)", 25 < lst.median() < 50, f"median={lst.median():.2f}")
    nd = rs["ndvi_mean"]
    check("NDVI within [-1, 1]", nd.dropna().between(-1, 1).all(), f"min={nd.min():.3f}, max={nd.max():.3f}")
    check("alias lst_c == lst_mean_c", rs["lst_c"].equals(rs["lst_mean_c"]))
    check("alias ndvi == ndvi_mean", rs["ndvi"].equals(rs["ndvi_mean"]))
    for c in FRACTION_COLS:
        if c in rs:
            v = rs[c].dropna()
            check(f"{c} within [0, 1]", v.between(0, 1).all(), f"n={len(v)}", critical=True)
    obs = rs["lst_observation_count"].dropna()
    check("lst_observation_count >= 1 where defined", (obs >= 1).all(), f"min={obs.min():.2f}")
    check("min LST <= mean <= max LST per grid",
          ((rs["lst_min_c"] <= rs["lst_mean_c"] + 1e-6) & (rs["lst_mean_c"] <= rs["lst_max_c"] + 1e-6)).all())

    # ---------------- missing-value semantics
    check("LST missing documented", True, f"{int(lst.isna().sum())} missing", critical=False)
    zero_lst = int((lst == 0).sum())
    check("no zero-filled LST", zero_lst == 0, zero_lst)
    dw_frac_all_missing = rs[["tree_fraction", "grass_fraction", "built_fraction"]].isna().all().all()
    check("DW class fractions are either computed or fully empty (never 0-filled placeholders)",
          dw_frac_all_missing or rs["tree_fraction"].notna().mean() > 0.99,
          "BLOCKED (all empty)" if dw_frac_all_missing else "computed", critical=True)
    if not dw_frac_all_missing:
        s = rs[["water_fraction", "tree_fraction", "grass_fraction", "flooded_vegetation_fraction",
                "crops_fraction", "shrub_fraction", "built_fraction", "bare_fraction"]].sum(axis=1)
        check("DW class fractions sum to ~1", ((s - 1).abs() < 0.02)[rs["tree_fraction"].notna()].all(),
              f"min={s.min():.3f}, max={s.max():.3f}")

    # ---------------- raster semantics
    with rasterio.open(LANDSAT_TIF) as src:
        lst_px = src.read(1); ndvi_px = src.read(2); val_px = src.read(5)
        outside = np.isnan(lst_px)
        nolst = lst_px == src.nodata
        check("Landsat raster: NaN = outside AOI, consistent across bands", (np.isnan(ndvi_px) == outside).all(),
              f"{int(outside.sum())} NaN px")
        check("Landsat raster: -9999 LST pixels are exactly lst_valid == 0", (nolst == (val_px == 0)).all(),
              f"{int(nolst.sum())} px without any clear LST observation inside AOI")
        fin = ndvi_px[np.isfinite(ndvi_px) & (ndvi_px != src.nodata)]
        check("Landsat raster: pixel NDVI within [-1, 1]", ((fin >= -1) & (fin <= 1)).all(),
              f"min={fin.min():.3f}, max={fin.max():.3f}")
        good = lst_px[np.isfinite(lst_px) & (lst_px != src.nodata)]
        check("Landsat raster: no ST fill (-124 C = 0 DN scaled) leaked", good.min() > 0, f"min={good.min():.2f}")

        # independent recomputation on 25 full interior cells
        grid = gpd.read_file(GRID_GPKG)
        full = grid[grid.geometry.area > 249_999].sample(25, random_state=42)
        r = rs.set_index(KEY)
        diffs_l, diffs_n = [], []
        for gid, geom in zip(full[KEY], full.geometry):
            if abs(geom.area - geom.envelope.area) > 1:  # only axis-aligned rectangles
                continue
            diffs_l.append(abs(window_mean(src, 1, geom.bounds) - r.loc[gid, "lst_mean_c"]))
            diffs_n.append(abs(window_mean(src, 2, geom.bounds) - r.loc[gid, "ndvi_mean"]))
        check("independent recomputation of LST mean (25 cells)", len(diffs_l) >= 20 and max(diffs_l) < 0.01,
              f"n={len(diffs_l)}, max |diff|={max(diffs_l):.5f} C")
        check("independent recomputation of NDVI mean (25 cells)", max(diffs_n) < 0.001,
              f"max |diff|={max(diffs_n):.6f}")
    with rasterio.open(DW_PROB_TIF) as src:
        diffs = []
        for gid, geom in zip(full[KEY], full.geometry):
            if abs(geom.area - geom.envelope.area) > 1:
                continue
            diffs.append(abs(window_mean(src, 1, geom.bounds) - r.loc[gid, "tree_prob_mean"]))
        check("independent recomputation of DW tree_prob_mean (25 cells)", max(diffs) < 1e-4,
              f"max |diff|={max(diffs):.6f}")

    # ---------------- outputs
    prob = rs[rs["rs_qa_flags"].notna() & (rs["rs_qa_flags"] != "")]
    prob = prob.merge(master[[KEY, "kota", "longitude", "latitude"]], on=KEY, how="left")
    prob[[KEY, "kota", "longitude", "latitude", "qa_area_km2", "rs_qa_flags", "lst_mean_c", "ndvi_mean",
          "lst_valid_fraction", "lst_observation_count", "lst_unc_mean_k", "tree_prob_mean"]].to_csv(PROBLEMS, index=False)
    print(f"wrote {PROBLEMS.relative_to(ROOT)} ({len(prob)} flagged grids)")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        g = gpd.read_file(GRID_GPKG)[[KEY, "geometry"]].merge(rs, on=KEY)
        fig, ax = plt.subplots(2, 3, figsize=(16, 11))
        spec = [("lst_mean_c", "LST mean of 2024 median composite (°C)", "inferno"),
                ("ndvi_mean", "NDVI mean of 2024 median composite", "YlGn"),
                ("lst_valid_fraction", "LST valid-pixel area fraction", "viridis"),
                ("lst_observation_count", "Mean clear LST observations / pixel (2024)", "cividis"),
                ("tree_prob_mean", "DW median trees probability (grid mean)", "Greens"),
                ("built_prob_mean", "DW median built probability (grid mean)", "Reds")]
        for a, (c, t, cm) in zip(ax.ravel(), spec):
            g.plot(column=c, ax=a, cmap=cm, legend=True, missing_kwds={"color": "lightgrey", "label": "missing"})
            a.set_title(t, fontsize=10); a.set_axis_off()
        fig.suptitle("Jakarta 500 m grid — remote sensing features, 2024 (QA preview; LST is land surface, not air temperature)")
        PREVIEW.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(PREVIEW, dpi=110, bbox_inches="tight")
        print(f"wrote {PREVIEW.relative_to(ROOT)}")
    except Exception as exc:  # preview is optional
        check("preview map", False, exc, critical=False)

    failed = [r for r in results if not r["ok"] and r["critical"]]
    QA_JSON.parent.mkdir(parents=True, exist_ok=True)
    QA_JSON.write_text(json.dumps({"n_checks": len(results), "n_critical_failed": len(failed),
                                   "checks": results}, indent=2), encoding="utf-8")
    print(f"\n{len(results)} checks, {len(failed)} critical failures")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
