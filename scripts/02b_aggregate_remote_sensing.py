"""Person 1 / Agent 1 -- aggregate 2024 remote-sensing composites to the 500 m master grid.

Inputs (real Google Earth Engine exports, produced by ``scripts/02_remote_sensing_gee.js``):

* ``data/processed/remote_sensing/jakarta_2024_lst_ndvi_qa.tif``
  Landsat 9 C2 L2 (LANDSAT/LC09/C02/T1_L2), 2024-01-01 .. 2025-01-01 (end exclusive),
  per-pixel *temporal median* of clear observations, 30 m, EPSG:32748, nodata -9999.
  Bands: lst_c (deg C), ndvi, lst_unc_k (median ST_QA, K), lst_obs (count of clear LST
  observations), lst_valid (1 = >=1 clear LST observation, 0 = none, nodata = outside AOI).
* ``data/processed/remote_sensing/jakarta_2024_trees_built_probability.tif``
  Dynamic World V1 (GOOGLE/DYNAMICWORLD/V1), same period, per-pixel *temporal median* of the
  per-image ``trees`` and ``built`` class probabilities, 10 m, EPSG:32748, nodata -9999.
* Optional ``data/processed/remote_sensing/jakarta_2024_dw_label_mode.tif`` from
  ``scripts/02c_dynamic_world_fractions_gee.js`` (per-pixel annual modal Dynamic World label,
  single band ``label_mode``, uint8 0..8, nodata 255). When present, class
  fractions (tree/grass/built/...) are computed; otherwise those columns stay empty (NaN).
* ``data/processed/grid_500m_jakarta.gpkg`` and ``data/processed/grid_master.csv`` (Person 2).

Spatial reduction: exact pixel-coverage-weighted statistics per grid polygon (``exactextract``):
a pixel that is 30 % inside a cell contributes with weight 0.3. Nodata pixels are ignored.
The grid polygons are already clipped to the five-city boundary, so edge cells are partial.

Output: ``data/processed/remote_sensing_grid.csv`` (+ ``.gpkg`` QA layer, ``.meta.json``).
Missing values are written as empty cells and are NEVER replaced by 0.

Run from the repository root::

    python scripts/02b_aggregate_remote_sensing.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from exactextract import exact_extract

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
RS_DIR = PROC / "remote_sensing"

LANDSAT_TIF = RS_DIR / "jakarta_2024_lst_ndvi_qa.tif"
DW_PROB_TIF = RS_DIR / "jakarta_2024_trees_built_probability.tif"
DW_LABEL_TIF = RS_DIR / "jakarta_2024_dw_label_mode.tif"
GRID_GPKG = PROC / "grid_500m_jakarta.gpkg"
GRID_CSV = PROC / "grid_master.csv"
OUT_CSV = PROC / "remote_sensing_grid.csv"
OUT_GPKG = PROC / "remote_sensing_grid.gpkg"
OUT_META = PROC / "remote_sensing_grid.meta.json"

EXPECTED_CRS = "EPSG:32748"
KEY = "grid_id"

LANDSAT_BANDS = ("lst_c", "ndvi", "lst_unc_k", "lst_obs", "lst_valid")
DW_PROB_BANDS = ("trees_prob", "built_prob")
# Dynamic World V1 label values (official class order).
DW_CLASSES = {
    0: "water", 1: "trees", 2: "grass", 3: "flooded_vegetation", 4: "crops",
    5: "shrub_and_scrub", 6: "built", 7: "bare", 8: "snow_and_ice",
}
DW_FRACTION_COLS = {  # output column -> DW class name
    "tree_fraction": "trees", "grass_fraction": "grass", "built_fraction": "built",
    "water_fraction": "water", "flooded_vegetation_fraction": "flooded_vegetation",
    "crops_fraction": "crops", "shrub_fraction": "shrub_and_scrub", "bare_fraction": "bare",
    "snow_ice_fraction": "snow_and_ice",
}

# QA thresholds (diagnostic flags only; no value is altered or clipped because of them).
MIN_VALID_FRACTION = 0.5     # flag cells where < 50 % of the cell area has a valid LST pixel
LOW_OBS = 5                  # flag cells whose mean clear-observation count is < 5
HIGH_UNC_K = 5.0             # flag cells whose mean median ST_QA uncertainty is > 5 K
EDGE_AREA_KM2 = 0.05         # flag tiny edge cells (< 0.05 km2 = 20 % of a full 0.25 km2 cell)
FRACTION_TOL = 1e-3          # tolerance for coverage-derived fractions slightly above 1


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_raster(path: Path, bands: tuple[str, ...]) -> dict:
    with rasterio.open(path) as src:
        crs = src.crs.to_string() if src.crs else None
        desc = tuple(src.descriptions)
        info = {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "crs": crs, "width": src.width, "height": src.height,
            "res_m": list(src.res), "bounds": list(src.bounds), "nodata": src.nodata,
            "bands": list(desc), "dtype": src.dtypes[0], "sha256": sha256(path),
        }
    if crs != EXPECTED_CRS:
        raise SystemExit(f"{path.name}: CRS {crs} != {EXPECTED_CRS}")
    if desc[: len(bands)] != bands:
        raise SystemExit(f"{path.name}: band names {desc} do not start with expected {bands}")
    return info


def load_grid() -> gpd.GeoDataFrame:
    grid = gpd.read_file(GRID_GPKG)
    master = pd.read_csv(GRID_CSV, dtype={KEY: "string"})
    if grid.crs is None or grid.crs.to_string() != EXPECTED_CRS:
        raise SystemExit(f"grid CRS {grid.crs} != {EXPECTED_CRS}")
    for name, ids in (("grid gpkg", grid[KEY]), ("grid_master.csv", master[KEY])):
        if ids.isna().any() or ids.duplicated().any():
            raise SystemExit(f"{name}: missing or duplicated grid_id")
    if set(grid[KEY]) != set(master[KEY]):
        raise SystemExit("grid_500m_jakarta.gpkg and grid_master.csv have different grid_id sets")
    # keep the master CSV row order
    grid = grid.set_index(KEY).loc[master[KEY].tolist()].reset_index()
    grid["geom_area_m2"] = grid.geometry.area
    return grid


def zonal(raster: Path, grid: gpd.GeoDataFrame, ops: list[str]) -> pd.DataFrame:
    df = exact_extract(str(raster), grid[[KEY, "geometry"]], ops, include_cols=[KEY], output="pandas")
    if len(df) != len(grid) or df[KEY].duplicated().any():
        raise SystemExit(f"zonal statistics on {raster.name} changed the number of rows")
    # exactextract names multi-band columns band_<i>_<op>; map to the GeoTIFF band descriptions
    with rasterio.open(raster) as src:
        desc = list(src.descriptions)
    if len(desc) > 1:
        ren = {}
        for i, name in enumerate(desc, start=1):
            for op in ops:
                ren[f"band_{i}_{op}"] = f"{name}_{op}"
        df = df.rename(columns=ren)
    else:
        df = df.rename(columns={op: f"{desc[0]}_{op}" for op in ops})
    return df


def aggregate_dw_labels(path: Path, grid: gpd.GeoDataFrame) -> pd.DataFrame:
    """Class area / clipped polygon area, including an explicit unknown-area share.

    exactextract's ``frac`` is conditional on valid labels. Multiply it by the
    valid-label area fraction before reporting whole-cell fractions. Conditional
    fractions are separately named ``*_valid``. With no supported labels, class
    fractions remain unknown, while missing-area fraction is 1.
    """
    with rasterio.open(path) as src:
        if src.crs is None or src.crs.to_string() != EXPECTED_CRS:
            raise ValueError("DW labels must use EPSG:32748")
        if src.count != 1 or src.nodata != 255 or src.dtypes != ("uint8",):
            raise ValueError("DW labels require one uint8 band and nodata=255")
        if src.res != (10.0, 10.0) or src.transform.b or src.transform.d:
            raise ValueError("DW labels require an unrotated 10 m grid")
        pixel_area = abs(src.res[0] * src.res[1])
    area = grid.set_index(KEY).geometry.area
    if not (area > 0).all():
        raise ValueError("DW fractions require positive polygon areas")
    lab = exact_extract(str(path), grid[[KEY, "geometry"]], ["unique", "frac", "count"],
                        include_cols=[KEY], output="pandas").set_index(KEY)
    ucol = next(c for c in lab if c.endswith("unique"))
    fcol = next(c for c in lab if c.endswith("frac"))
    ccol = next(c for c in lab if c.endswith("count"))
    support = lab[ccol] * pixel_area / area
    if (support > 1 + FRACTION_TOL).any():
        raise ValueError("DW label support exceeds polygon area")
    support = support.clip(0, 1)
    result = pd.DataFrame(index=lab.index)
    for col in DW_FRACTION_COLS:
        result[col + "_valid"] = 0.0
    by_class = {cls: col for col, cls in DW_FRACTION_COLS.items()}
    for gid, uniq, frac in zip(lab.index, lab[ucol], lab[fcol]):
        for value, fraction in zip(np.atleast_1d(uniq), np.atleast_1d(frac)):
            if value not in DW_CLASSES:
                raise ValueError(f"Unexpected DW label {value} in {gid}")
            result.loc[gid, by_class[DW_CLASSES[int(value)]] + "_valid"] += float(fraction)
    result.loc[support == 0, :] = np.nan
    for col in DW_FRACTION_COLS:
        result[col] = result[col + "_valid"] * support
    result["dw_label_valid_fraction"] = support
    result["dw_label_missing_fraction"] = 1 - support
    return result


def aggregate(grid: gpd.GeoDataFrame, pixel_area_l8: float, pixel_area_dw: float) -> tuple[pd.DataFrame, dict]:
    notes: dict = {}
    area = grid.set_index(KEY)["geom_area_m2"]

    # ---------------- Landsat 9: LST / NDVI / QA bands
    ls = zonal(LANDSAT_TIF, grid, ["mean", "stdev", "min", "max", "count"]).set_index(KEY)
    out = pd.DataFrame(index=grid[KEY])
    out["lst_mean_c"] = ls["lst_c_mean"]
    out["lst_std_c"] = ls["lst_c_stdev"]
    out["lst_min_c"] = ls["lst_c_min"]
    out["lst_max_c"] = ls["lst_c_max"]
    out["ndvi_mean"] = ls["ndvi_mean"]
    out["ndvi_std"] = ls["ndvi_stdev"]
    out["lst_unc_mean_k"] = ls["lst_unc_k_mean"]
    out["lst_observation_count"] = ls["lst_obs_mean"]
    out["lst_observation_min"] = ls["lst_obs_min"]
    # coverage-weighted pixel counts -> area fractions of the (clipped) cell polygon
    out["lst_valid_fraction"] = ls["lst_c_count"] * pixel_area_l8 / area
    out["ndvi_valid_fraction"] = ls["ndvi_count"] * pixel_area_l8 / area
    out["landsat_footprint_fraction"] = ls["lst_valid_count"] * pixel_area_l8 / area

    # ---------------- Dynamic World: median class probabilities
    dw = zonal(DW_PROB_TIF, grid, ["mean", "count"]).set_index(KEY)
    out["tree_prob_mean"] = dw["trees_prob_mean"]
    out["built_prob_mean"] = dw["built_prob_mean"]
    out["dw_valid_fraction"] = dw["trees_prob_count"] * pixel_area_dw / area

    # ---------------- Dynamic World: class fractions from the annual modal label (optional)
    if DW_LABEL_TIF.exists():
        labels = aggregate_dw_labels(DW_LABEL_TIF, grid)
        out = out.join(labels)
        notes["dw_fraction_status"] = "computed from annual modal Dynamic World label"
    else:
        for col in DW_FRACTION_COLS:
            out[col] = np.nan
            out[col + "_valid"] = np.nan
        out["dw_label_valid_fraction"] = np.nan
        out["dw_label_missing_fraction"] = np.nan
        notes["dw_fraction_status"] = (
            "BLOCKED: jakarta_2024_dw_label_mode.tif not available; run "
            "scripts/02c_dynamic_world_fractions_gee.js in Earth Engine and re-run this script"
        )

    # fractions derived from pixel coverage can exceed 1 by floating-point error only
    frac_cols = ["lst_valid_fraction", "ndvi_valid_fraction", "landsat_footprint_fraction",
                 "dw_valid_fraction", "dw_label_valid_fraction"]
    for c in frac_cols:
        over = out[c] > 1 + FRACTION_TOL
        if over.any():
            raise SystemExit(f"{c}: {int(over.sum())} cells exceed 1 beyond tolerance (CRS/area mismatch?)")
        out[c] = out[c].clip(upper=1.0)

    # ---------------- compatibility aliases for jhim / dashboard (Agent 3 contract: lst_c, ndvi)
    out["lst_c"] = out["lst_mean_c"]
    out["ndvi"] = out["ndvi_mean"]

    # ---------------- QA flags (diagnostics only)
    out["qa_area_km2"] = area / 1e6
    out["qa_area_m2"] = area
    flags = pd.DataFrame(index=out.index)
    flags["no_lst"] = out["lst_mean_c"].isna()
    flags["partial_lst"] = out["lst_valid_fraction"] < MIN_VALID_FRACTION
    flags["low_obs"] = out["lst_observation_count"] < LOW_OBS
    flags["high_unc"] = out["lst_unc_mean_k"] > HIGH_UNC_K
    flags["edge_cell"] = out["qa_area_km2"] < EDGE_AREA_KM2
    flags["footprint_gap"] = out["landsat_footprint_fraction"] < 1 - 0.02
    out["rs_qa_flags"] = flags.apply(lambda r: ";".join(k for k, v in r.items() if bool(v)), axis=1)
    out["rs_qa_ok"] = ~(flags["no_lst"] | flags["partial_lst"] | flags["low_obs"] | flags["high_unc"])
    out = out.reset_index().rename(columns={"index": KEY})
    return out, notes


COLUMN_ORDER = [
    KEY, "lst_mean_c", "ndvi_mean", "tree_fraction", "grass_fraction", "built_fraction",
    "lst_valid_fraction", "lst_observation_count",
    "lst_std_c", "lst_min_c", "lst_max_c", "lst_unc_mean_k", "lst_observation_min",
    "ndvi_std", "ndvi_valid_fraction", "landsat_footprint_fraction",
    "tree_prob_mean", "built_prob_mean", "dw_valid_fraction",
    "water_fraction", "flooded_vegetation_fraction", "crops_fraction", "shrub_fraction",
    "bare_fraction", "dw_label_valid_fraction",
    "qa_area_km2", "rs_qa_flags", "rs_qa_ok", "lst_c", "ndvi",
    "qa_area_m2", "snow_ice_fraction", "dw_label_missing_fraction",
    *[col + "_valid" for col in DW_FRACTION_COLS],
]

ROUND = {
    "lst_mean_c": 3, "lst_std_c": 3, "lst_min_c": 3, "lst_max_c": 3, "lst_c": 3,
    "ndvi_mean": 4, "ndvi_std": 4, "ndvi": 4, "lst_unc_mean_k": 3,
    "lst_observation_count": 2, "lst_observation_min": 0,
}


def write_grid_csv(out: pd.DataFrame, path: Path) -> None:
    """Keep legacy measurement precision, but do not round positive sliver areas to 0."""
    serial = out.copy()
    for col in ("qa_area_km2", "qa_area_m2"):
        serial[col] = serial[col].map(lambda x: format(x, ".15g"))
    serial.to_csv(path, index=False, float_format="%.6g", na_rep="")


def summary(df: pd.DataFrame) -> dict:
    s: dict = {"n_rows": int(len(df)), "n_unique_grid_id": int(df[KEY].nunique())}
    for c in COLUMN_ORDER:
        if c in (KEY, "rs_qa_flags") or c not in df:
            continue
        v = pd.to_numeric(df[c], errors="coerce").astype(float)
        s[c] = {
            "n_missing": int(v.isna().sum()),
            **({} if v.notna().sum() == 0 else {
                "min": float(v.min()), "p5": float(v.quantile(0.05)), "median": float(v.median()),
                "mean": float(v.mean()), "p95": float(v.quantile(0.95)), "max": float(v.max())}),
        }
    flags = df["rs_qa_flags"].fillna("")
    s["qa_flag_counts"] = {f: int(flags.str.split(";").apply(lambda x: f in x).sum())
                           for f in ("no_lst", "partial_lst", "low_obs", "high_unc", "edge_cell", "footprint_gap")}
    s["rs_qa_ok_true"] = int(df["rs_qa_ok"].sum())
    return s


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--no-gpkg", action="store_true", help="skip the GeoPackage QA layer")
    ap.add_argument("--output-dir", type=Path, default=PROC, help="isolated output directory (default: canonical processed folder)")
    args = ap.parse_args(argv)

    landsat_info = check_raster(LANDSAT_TIF, LANDSAT_BANDS)
    dw_info = check_raster(DW_PROB_TIF, DW_PROB_BANDS)
    grid = load_grid()
    px_l8 = abs(landsat_info["res_m"][0] * landsat_info["res_m"][1])
    px_dw = abs(dw_info["res_m"][0] * dw_info["res_m"][1])

    out, notes = aggregate(grid, px_l8, px_dw)
    out = out[COLUMN_ORDER]
    for c, d in ROUND.items():
        out[c] = out[c].round(d)

    if len(out) != len(grid) or out[KEY].tolist() != grid[KEY].tolist():
        raise SystemExit("output rows do not match the master grid one-to-one")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    out_csv = args.output_dir / OUT_CSV.name
    out_gpkg = args.output_dir / OUT_GPKG.name
    out_meta = args.output_dir / OUT_META.name
    write_grid_csv(out, out_csv)
    if not args.no_gpkg:
        g = grid[[KEY, "kota", "geometry"]].merge(out, on=KEY, how="left", validate="one_to_one")
        g.to_file(out_gpkg, layer="remote_sensing_grid", driver="GPKG")

    meta = {
        "dataset": "remote_sensing_grid",
        "owner": "Person 1 / Agent 1 (remote sensing workstream)",
        "built_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "script": "scripts/02b_aggregate_remote_sensing.py",
        "period": {"start": "2024-01-01", "end_exclusive": "2025-01-01"},
        "temporal_reducer": {
            "landsat": "per-pixel median of clear-sky Landsat 9 C2 L2 observations (QA_PIXEL bits 0-5 == 0, QA_RADSAT == 0)",
            "dynamic_world_probabilities": "per-pixel median of per-image Dynamic World class probabilities",
            "dynamic_world_label": "per-pixel mode of per-image Dynamic World label (only if label raster present)",
        },
        "spatial_reducer": "exact pixel-coverage-weighted statistics per clipped 500 m grid polygon (exactextract); nodata ignored",
        "grid": {"path": "data/processed/grid_500m_jakarta.gpkg", "crs": EXPECTED_CRS, "n_cells": int(len(grid)),
                 "sha256": sha256(GRID_GPKG), "master_csv_sha256": sha256(GRID_CSV)},
        "inputs": {"landsat": landsat_info, "dynamic_world_probabilities": dw_info,
                   "dynamic_world_label": check_raster(DW_LABEL_TIF, ("label_mode",)) if DW_LABEL_TIF.exists() else None},
        "implementation_sha256": sha256(Path(__file__)),
        "dw_fraction_denominators": {
            "*_fraction": "class-labelled area / whole clipped polygon area; NaN with no valid label",
            "*_fraction_valid": "class-labelled area / valid-labelled area; NaN with no valid label",
            "dw_label_valid_fraction": "valid-labelled area / whole clipped polygon area",
            "dw_label_missing_fraction": "1 - dw_label_valid_fraction; NaN if entire label export absent",
            "sum_classes": "all nine classes, including snow_ice_fraction, sum to dw_label_valid_fraction",
        },
        "qa_thresholds": {"min_valid_fraction": MIN_VALID_FRACTION, "low_obs": LOW_OBS,
                          "high_unc_k": HIGH_UNC_K, "edge_area_km2": EDGE_AREA_KM2},
        "missing_value_semantics": "empty cell = not computable from valid pixels; never imputed, never zero-filled",
        "notes": notes,
        "summary": summary(out),
    }
    out_meta.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(meta["summary"], indent=1)[:4000])
    print(f"wrote {out_csv} ({len(out)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
