"""RS-01/DW-01: offline evidence from frozen real rasters; never invent acquisition records.

Build the revised grid first with 02b --output-dir data/processed/remote_sensing_remediated.
This command preserves the audited canonical grid and all source rasters.
--verify checks the recorded file hashes without rewriting evidence.
--compare-landsat FILE compares a future GEE replay to the frozen raster, without replacing it.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from shapely.geometry import box
from rasterio.windows import from_bounds

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data/processed"
QA = ROOT / "outputs/qa/agent1_remediation"
DOCS = ROOT / "docs"
REVISED = PROC / "remote_sensing_remediated"
MANIFEST = DOCS / "remote_sensing_export_manifest.json"
LANDSAT = PROC / "remote_sensing/jakarta_2024_lst_ndvi_qa.tif"
DW = PROC / "remote_sensing/jakarta_2024_trees_built_probability.tif"
SCENE_FIELDS = ["dataset_id", "image_id", "system_index", "acquired_at_utc", "wrs_path", "wrs_row",
                "processing_level", "product_id", "date_product_generated", "recipe_id"]


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def polygon_band_stats(src, band, geom):
    """Independent Shapely intersections: no exactextract, includes tiny/clipped cells."""
    win = from_bounds(*geom.bounds, transform=src.transform)
    c0 = max(0, int(np.floor(win.col_off)))
    r0 = max(0, int(np.floor(win.row_off)))
    c1 = min(src.width, int(np.ceil(win.col_off + win.width)))
    r1 = min(src.height, int(np.ceil(win.row_off + win.height)))
    a = src.read(band, window=((r0, r1), (c0, c1)))
    total, area = 0.0, 0.0
    for rr, cc in np.ndindex(a.shape):
        v = float(a[rr, cc])
        if not np.isfinite(v) or v == src.nodata:
            continue
        x0, y0 = src.transform * (c0 + cc, r0 + rr)
        x1, y1 = src.transform * (c0 + cc + 1, r0 + rr + 1)
        overlap = geom.intersection(box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))).area
        area += overlap
        total += overlap * v
    return (total / area if area else None), area


def compare_rasters(old, new):
    """Array comparison requires identical grids, band names and nodata semantics."""
    with rasterio.open(old) as a, rasterio.open(new) as b:
        if (a.crs, a.transform, a.shape, a.count, a.descriptions, a.nodata) != (
                b.crs, b.transform, b.shape, b.count, b.descriptions, b.nodata):
            raise ValueError("Replay grid/bands/nodata differ; harmonize explicitly before comparison")
        result = []
        for band in range(1, a.count + 1):
            x, y = a.read(band), b.read(band)
            vx = np.isfinite(x) & (x != a.nodata)
            vy = np.isfinite(y) & (y != b.nodata)
            both = vx & vy
            d = y[both].astype(float) - x[both].astype(float)
            result.append({"band": a.descriptions[band - 1], "valid_mask_changed_pixels": int((vx != vy).sum()),
                           "outside_nan_changed_pixels": int((np.isnan(x) != np.isnan(y)).sum()),
                           "shared_valid_pixels": int(both.sum()),
                           "max_abs_difference": float(np.max(np.abs(d))) if d.size else None,
                           "mean_difference": float(d.mean()) if d.size else None})
    return result


def validate_scene_manifest(path):
    """A header-only placeholder is explicitly NOT acquisition verification."""
    rows = list(csv.DictReader(Path(path).open(encoding="utf-8")))
    if not rows:
        return {"state": "BLOCKED", "n_scenes": 0, "reason": "No recovered scene records; zero rows is not zero acquisitions"}
    identities = set()
    counts = {}
    for row in rows:
        if row["dataset_id"] not in ("LANDSAT/LC09/C02/T1_L2", "GOOGLE/DYNAMICWORLD/V1"):
            raise ValueError("Unexpected scene collection")
        stamp = pd.Timestamp(row["acquired_at_utc"])
        if stamp.tzinfo is None or not pd.Timestamp("2024-01-01T00:00:00Z") <= stamp < pd.Timestamp("2025-01-01T00:00:00Z"):
            raise ValueError("Scene timestamp outside declared UTC period")
        identity = (row["dataset_id"], row["image_id"])
        if not row["image_id"].startswith(row["dataset_id"] + "/") or identity in identities:
            raise ValueError("Invalid or duplicate scene ID")
        if not row["recipe_id"]:
            raise ValueError("Scene record needs a replay recipe ID")
        if row["dataset_id"].startswith("LANDSAT") and (
                row["processing_level"] != "L2SP" or not row["wrs_path"] or not row["wrs_row"]):
            raise ValueError("Landsat processing level/WRS metadata missing")
        identities.add(identity)
        counts[row["dataset_id"]] = counts.get(row["dataset_id"], 0) + 1
    missing = set(("LANDSAT/LC09/C02/T1_L2", "GOOGLE/DYNAMICWORLD/V1")) - set(counts)
    return {"state": "PARTIAL" if missing else "DATES_VALIDATED_ONLY", "n_scenes": len(rows),
            "collection_counts": counts, "reason": "Date predicates checked; export/task/AOI linkage still requires operator evidence"}


def verify_manifest(path=MANIFEST):
    manifest = json.loads(path.read_text(encoding="utf-8"))
    failures = []
    for record in manifest["files"]:
        p = ROOT / record["path"]
        if not p.is_file() or sha256(p) != record["sha256"]:
            failures.append(record["path"])
    if failures:
        raise ValueError("Manifest hash mismatch: " + ", ".join(failures))
    return len(manifest["files"])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--compare-landsat", type=Path)
    args = ap.parse_args(argv)
    if args.verify:
        print(f"PASS: {verify_manifest()} recorded hashes match; acquisition status remains BLOCKED")
        return 0
    if args.compare_landsat:
        result = {"baseline_sha256": sha256(LANDSAT), "replay_sha256": sha256(args.compare_landsat),
                  "bands": compare_rasters(LANDSAT, args.compare_landsat),
                  "warning": "Matching arrays alone do not establish historical task provenance"}
        write_json(QA / "landsat_replay_comparison.json", result)
        print(json.dumps(result, indent=2))
        return 0

    QA.mkdir(parents=True, exist_ok=True)
    base = pd.read_csv(PROC / "remote_sensing_grid.csv").set_index("grid_id")
    revised = pd.read_csv(REVISED / "remote_sensing_grid.csv").set_index("grid_id")
    grid = gpd.read_file(PROC / "grid_500m_jakarta.gpkg").set_index("grid_id").loc[base.index]
    master = pd.read_csv(PROC / "grid_master.csv").set_index("grid_id").loc[base.index]
    sp = pd.read_csv(PROC / "spatial_features.csv").set_index("grid_id").loc[base.index]
    support = base[["lst_mean_c", "ndvi_mean", "lst_valid_fraction", "lst_observation_count",
                    "lst_observation_min", "lst_unc_mean_k", "rs_qa_flags", "rs_qa_ok"]].copy()
    support["clipped_area_m2"] = grid.geometry.area
    support["lst_valid_area_m2_from_serialized_fraction"] = support["clipped_area_m2"] * support["lst_valid_fraction"]
    support["clipped_over_nominal_area"] = grid.geometry.area / 250000
    support["kota"] = master["kota"]
    support["acquisition_dates_verified"] = False
    support["monthly_support_state"] = "UNAVAILABLE_FROM_TEMPORAL_MEDIAN_EXPORT"
    support.to_csv(ROOT / "outputs/qa/rs_temporal_support.csv")
    support.groupby("kota").agg(
        n_grids=("lst_observation_count", "size"),
        mean_clear_observations=("lst_observation_count", "mean"),
        median_clear_observations=("lst_observation_count", "median"),
        min_clear_observations=("lst_observation_count", "min"),
        max_clear_observations=("lst_observation_count", "max"),
        min_valid_fraction=("lst_valid_fraction", "min"),
    ).to_csv(QA / "rs_temporal_support_by_city.csv")
    policies = pd.DataFrame(index=base.index)
    policies["data_delivered"] = base[["lst_mean_c", "ndvi_mean"]].notna().all(axis=1)
    policies["baseline_valid_ge_0_5"] = base["lst_valid_fraction"] >= 0.5
    policies["exploratory_valid_ge_0_25"] = base["lst_valid_fraction"] >= 0.25
    policies["exploratory_include_flagged"] = policies["data_delivered"]
    policies["exploratory_strict_rs_qa"] = base["rs_qa_ok"]
    policies["legacy_route_present"] = sp["park_distance_m"].notna()
    policies.to_csv(QA / "rs_qa_policy_support.csv")

    changed = []
    for col in base:
        same = base[col].eq(revised[col]) | (base[col].isna() & revised[col].isna())
        changed.append({"column": col, "changed_rows": int((~same).sum())})
    pd.DataFrame(changed).to_csv(QA / "baseline_revised_comparison.csv", index=False)
    if any(row["changed_rows"] for row in changed if row["column"] != "qa_area_km2"):
        raise ValueError("Unexpected change to an audited baseline value")

    # Check actual local M1-M4 calculations on the fixed legacy comparison set.
    # This does not select a new eligibility rule or use repaired demographics.
    sys.path.insert(0, str(ROOT))
    from jhim import config as model_config, models
    fixed = policies["baseline_valid_ge_0_5"] & policies["legacy_route_present"]
    frames = []
    for rs in (base, revised):
        frame = sp.loc[fixed, ["population", "pop_child", "pop_elderly", "park_distance_m"]].copy()
        frame[["lst_c", "ndvi"]] = rs.loc[fixed, ["lst_c", "ndvi"]]
        frame["grid_id"] = frame.index
        frames.append(frame)
    rank_checks = []
    for model, weights in model_config.MODELS.items():
        old_score, old_rank = models.score_rank(frames[0], weights)
        new_score, new_rank = models.score_rank(frames[1], weights)
        if not old_score.equals(new_score) or not old_rank.equals(new_rank):
            raise ValueError("Revised RS input unexpectedly changes fixed-set model results")
        for fraction in (.05, .10, .20):
            budget = models.n_top(int(fixed.sum()), fraction)
            old_top = set(old_rank[old_rank <= budget].index)
            new_top = set(new_rank[new_rank <= budget].index)
            rank_checks.append({"model": model, "n_fixed_legacy_ids": int(fixed.sum()), "top_fraction": fraction,
                                "budget": budget, "retained": len(old_top & new_top), "entered": len(new_top - old_top),
                                "left": len(old_top - new_top), "jaccard": len(old_top & new_top) / len(old_top | new_top),
                                "max_abs_score_change": float((old_score - new_score).abs().max()),
                                "changed_ranks": int((old_rank != new_rank).sum()),
                                "scope": "RS-input-only comparison; legacy demographics; not final corrected scientific results"})
    pd.DataFrame(rank_checks).to_csv(QA / "rs_input_revision_model_effect.csv", index=False)

    # Four eastern support gaps, six smallest polygons, and 25 deterministic interior cells.
    gap_ids = ["JKT_R037_C061", "JKT_R037_C062", "JKT_R038_C061", "JKT_R038_C062"]
    ids = list(dict.fromkeys(gap_ids + grid.geometry.area.nsmallest(6).index.tolist()
                            + grid[grid.geometry.area > 249999].sample(25, random_state=42).index.tolist()))
    intersections = []
    with rasterio.open(LANDSAT) as ls, rasterio.open(DW) as dw:
        for gid in ids:
            geom = grid.loc[gid, "geometry"]
            for src, band, col, tolerance in [(ls, 1, "lst_mean_c", .00051), (ls, 2, "ndvi_mean", .000051),
                                              (dw, 1, "tree_prob_mean", .000001), (dw, 2, "built_prob_mean", .000001)]:
                value, valid_area = polygon_band_stats(src, band, geom)
                saved = revised.loc[gid, col]
                delta = abs(value - saved) if value is not None and pd.notna(saved) else None
                passed = (value is None and pd.isna(saved)) or (delta is not None and delta <= tolerance)
                intersections.append({"grid_id": gid, "variable": col, "independent_mean": value,
                                      "reported_mean": saved, "valid_area_m2": valid_area,
                                      "polygon_area_m2": geom.area, "independent_valid_fraction": valid_area / geom.area,
                                      "absolute_difference": delta, "tolerance": tolerance, "passed": passed})
    pd.DataFrame(intersections).to_csv(QA / "independent_pixel_checks.csv", index=False)
    if not all(row["passed"] for row in intersections):
        raise ValueError("Independent pixel checks failed")

    scene_path = DOCS / "remote_sensing_scene_manifest.csv"
    if not scene_path.exists():
        with scene_path.open("w", newline="", encoding="utf-8") as stream:
            csv.writer(stream).writerow(SCENE_FIELDS)
    monthly_path = QA / "rs_monthly_temporal_support.csv"
    if not monthly_path.exists():
        pd.DataFrame([{"month_utc": f"2024-{month:02d}", "scene_count": None,
                       "clear_pixel_observations": None, "valid_area_m2": None,
                       "state": "BLOCKED_GEE_ACQUISITION_EXPORT_REQUIRED"} for month in range(1, 13)]).to_csv(monthly_path, index=False)

    package_names = ["numpy", "pandas", "geopandas", "pyogrio", "shapely", "pyproj", "rasterio",
                     "exactextract", "matplotlib", "pytest", "earthengine-api"]
    environment = {"python": platform.python_version(), "platform": platform.platform(),
                   "packages": {name: importlib.metadata.version(name) for name in package_names}}
    write_json(QA / "environment.json", environment)
    summary = {"n_grids": len(base), "independent_values_checked": len(intersections),
               "all_independent_values_pass": True, "changed_legacy_columns": [r for r in changed if r["changed_rows"]],
               "new_columns": sorted(set(revised) - set(base)),
               "policy_counts": {c: {"all_grids": int(policies[c].sum()),
                                     "legacy_route_present": int((policies[c] & policies["legacy_route_present"]).sum())}
                                 for c in policies if c.startswith(("baseline_", "exploratory_"))},
               "scene_provenance": validate_scene_manifest(scene_path)}
    summary_path = ROOT / "outputs/qa/agent1_remediation_summary.json"
    write_json(summary_path, summary)
    inputs = [LANDSAT, DW, PROC / "grid_500m_jakarta.gpkg", PROC / "grid_master.csv", PROC / "spatial_features.csv",
              PROC / "jakarta_5kota.gpkg", PROC / "remote_sensing_grid.csv", PROC / "remote_sensing_grid.gpkg",
              PROC / "remote_sensing_grid.meta.json", ROOT / "requirements-remote-sensing.txt"]
    owned_sources = list((ROOT / "scripts").glob("02*")) + list((ROOT / "tests").glob("test_remote_sensing*.py"))
    owned_sources += [DOCS / name for name in ("landsat_metadata.json", "dynamic_world_metadata.json",
                      "landsat_quality_report.md", "remote_sensing_deliverable_status.md", "remote_sensing_reproduction.md")]
    owned_sources += [ROOT / "handoff/AGENT1_HANDOFF.md", ROOT / "handoff/REMEDIATION_AGENT1.md"]
    owned_sources += [ROOT / "jhim/config.py", ROOT / "jhim/models.py"]
    evidence = [p for p in QA.rglob("*") if p.is_file()]
    files = sorted(set(inputs + owned_sources + evidence + [scene_path, ROOT / "outputs/qa/rs_temporal_support.csv"]
                       + [summary_path] + list(REVISED.glob("remote_sensing_grid.*"))))
    manifest = {
        "schema_version": 1, "issue_ids": ["RS-01", "DW-01"],
        "acquisition_status": "BLOCKED_ORIGINAL_SCENE_TASK_AOI_RECORDS_UNRECOVERED",
        "local_reproduction_status": "PASS_FROZEN_RASTERS_TO_GRID",
        "declared_period": {"start": "2024-01-01", "end_exclusive": "2025-01-01"},
        "scene_manifest_validation": validate_scene_manifest(scene_path),
        "estimand": "clipped-cell area-weighted mean over valid pixels of per-pixel clear-sky morning temporal-median land surface temperature",
        "claims_excluded": ["annual air temperature", "continuous or annual-mean heat exposure", "individual heat dose",
                            "seasonally representative climate", "independently verified 2024 acquisition origins"],
        "original_exports": [
            {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(path),
             "task_id": None, "processing_date_utc": None, "scene_ids_verified": False,
             "intended_collection": collection, "recipe_file": "scripts/02_remote_sensing_gee.js",
             "recipe_relation": "intended recipe; historical execution identity unverified",
             "export_parameters_from_recipe": {"crs": "EPSG:32748", "scale_m": scale, "nodata": -9999,
                                                "folder": "Jakarta_Heat_Project", "region": "GEE AOI asset geometry",
                                                "file_format": "GeoTIFF", "max_pixels": 10000000000}}
            for path, collection, scale in [(LANDSAT, "LANDSAT/LC09/C02/T1_L2", 30), (DW, "GOOGLE/DYNAMICWORLD/V1", 10)]],
        "aoi": {"asset_id": "projects/nodemailer-mailer/assets/jakarta_5kota", "gee_geometry_sha256": None,
                "asset_version": None, "local_boundary_path": "data/processed/jakarta_5kota.gpkg",
                "local_boundary_sha256": sha256(PROC / "jakarta_5kota.gpkg"),
                "equivalence_to_gee_asset": "UNVERIFIED; local hash is not a historical GEE AOI hash"},
        "credentials": {"earthengine_file_present": (Path.home() / ".config/earthengine/credentials").is_file(),
                        "gcloud_adc_file_present": (Path.home() / "AppData/Roaming/gcloud/application_default_credentials.json").is_file(),
                        "scope": "presence only; no credential contents read; initialization probe recorded in handoff"},
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_state": "uncommitted remediation identified by per-file hashes; not an integrated release",
        "environment": environment,
        "files": [{"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(path)} for path in files if path.is_file()],
        "outstanding": ["authorized GEE execution or original task archive", "scene IDs/dates and monthly clear support",
                        "actual task IDs, processing date and exported/versioned AOI", "coordinator TM-01/thermal-estimand and R3 scope decisions",
                        "Agent 3 fixed-model reranking for QA policies (RS-02)"]}
    write_json(MANIFEST, manifest)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
