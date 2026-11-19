"""Capture/compare two full frozen-candidate runs by table content and GIS geometry.

Usage (same source/config/inputs/runtime):
    python scripts/check_agent3_replay.py --capture      # after a complete, fresh run 1
    python scripts/run_agent3_remediation.py --audit ...  # run 2
    python scripts/check_agent3_replay.py                # compare run 2 against run 1

Guards: both runs must be complete (spatial included) and fresh by `manifest_status`; the compared
manifests must record the same implementation, config, inputs and actual runtime; run 2 must have a
different `built_at` (a real second execution, not a self-comparison); the compared file sets must be
identical. Tables compare at atol=rtol=1e-12, JSON metadata exactly (build timestamps excluded),
geometry by WKB. Container/PNG/SVG byte identity is reported but is not scientific equivalence.
"""
import argparse
import json
import os
import shutil
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from jhim import config as C
from jhim.provenance import implementation_identity, manifest_status, scientific_config
from jhim.util import sha256, write_json

SNAPSHOT = ROOT / "outputs/remediation/qa/replay_snapshot"
REPORT = ROOT / "outputs/remediation/qa/replay_verification.json"
MODELING = ROOT / "data/processed/modeling_remediation"
TABLE_DIRS = [MODELING, ROOT / "outputs/remediation/tables", ROOT / "outputs/remediation/paper"]
GIS_DIR = ROOT / "outputs/remediation/gis"
FIGURE_DIR = ROOT / "outputs/remediation/figures"
# Files that legitimately embed per-run identity (timestamps, absolute output hashes) are not table content.
EXCLUDED = {"output_sha256_manifest.csv", "run_manifest.json"}
VOLATILE_JSON_KEYS = {"built_at"}
EXPECTED_RUNTIME = {"permutations": 999, "high_permutations": 9999, "seed": C.SEED, "skip_spatial": False}


def candidate_paths():
    # Same environment as jhim.remediation.run so input identities resolve to the frozen evidence.
    inputs = ROOT / "data/processed/remediation_inputs"
    os.environ["JHIM_INPUT_DIR"] = str(inputs)
    os.environ.pop("JHIM_RS_PATH", None)
    os.environ["JHIM_DEMOGRAPHIC_SUPPORT"] = str(inputs / "demographic_support.csv")
    os.environ.pop("JHIM_DEMOGRAPHIC_CORRECTED", None)
    return C.RemediationPaths(root=ROOT)


def tracked_files():
    tables = sorted(p for d in TABLE_DIRS for p in d.glob("*") if p.suffix in (".csv", ".json") and p.name not in EXCLUDED)
    return tables, sorted(GIS_DIR.glob("*.gpkg")), sorted(FIGURE_DIR.glob("*.*"))


def rel(p):
    return Path(p).resolve().relative_to(ROOT).as_posix()


def fresh_manifest():
    man = json.loads((MODELING / "run_manifest.json").read_text(encoding="utf-8"))
    stale = manifest_status(candidate_paths(), man, EXPECTED_RUNTIME)
    if stale:
        raise AssertionError(f"Candidate manifest is not fresh/complete: {stale}")
    return man


def strip(obj):
    if isinstance(obj, dict):
        return {k: strip(v) for k, v in obj.items() if k not in VOLATILE_JSON_KEYS}
    if isinstance(obj, list):
        return [strip(v) for v in obj]
    return obj


def capture():
    man = fresh_manifest()
    if SNAPSHOT.exists():
        shutil.rmtree(SNAPSHOT)
    tables, gis, figures = tracked_files()
    for p in [*tables, *gis]:
        dest = SNAPSHOT / rel(p)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, dest)
    write_json(SNAPSHOT / "identity.json", {
        "built_at": man["built_at"], "implementation": man["implementation"], "config": man["config"],
        "inputs": man["inputs"], "runtime": man["runtime"],
        "current_implementation_sha256": implementation_identity()["sha256"],
        "tables": [rel(p) for p in tables], "gis": [rel(p) for p in gis],
        "figure_sha256": {rel(p): sha256(p) for p in figures}})
    print(f"Captured run built_at={man['built_at']}: {len(tables)} tables/metadata, {len(gis)} GPKG, {len(figures)} figure hashes")


def compare():
    first = json.loads((SNAPSHOT / "identity.json").read_text(encoding="utf-8"))
    man = fresh_manifest()
    checks = {}
    if man["built_at"] == first["built_at"]:
        raise AssertionError("Second run not executed: candidate manifest built_at equals the captured run")
    checks["second_run_built_at"] = man["built_at"]
    for key in ("implementation", "config", "inputs", "runtime"):
        if man[key] != first[key]:
            raise AssertionError(f"{key} differs between compared runs")
    if implementation_identity() != man["implementation"]:
        raise AssertionError("Source changed after the second run")
    if scientific_config() != man["config"]:
        raise AssertionError("Config changed after the second run")
    tables, gis, figures = tracked_files()
    if [rel(p) for p in tables] != first["tables"] or [rel(p) for p in gis] != first["gis"]:
        raise AssertionError("Compared output file sets differ between runs")
    max_abs = 0.0
    for p in tables:
        old_path = SNAPSHOT / rel(p)
        if p.suffix == ".json":
            a = strip(json.loads(old_path.read_text(encoding="utf-8")))
            b = strip(json.loads(p.read_text(encoding="utf-8")))
            if a != b:
                raise AssertionError(f"JSON content differs: {rel(p)}")
            continue
        before, after = pd.read_csv(old_path, low_memory=False), pd.read_csv(p, low_memory=False)
        pd.testing.assert_frame_equal(before, after, check_dtype=False, atol=1e-12, rtol=1e-12, obj=rel(p))
        num = before.select_dtypes("number").columns
        if len(num):
            diff = (before[num].astype(float) - after[num].astype(float)).abs().to_numpy()
            if np.isfinite(diff).any():
                max_abs = max(max_abs, float(np.nanmax(np.where(np.isfinite(diff), diff, np.nan))))
    geometry_rows = {}
    for p in gis:
        old = gpd.read_file(SNAPSHOT / rel(p)).sort_values("grid_id").reset_index(drop=True)
        new = gpd.read_file(p).sort_values("grid_id").reset_index(drop=True)
        if old.crs != new.crs:
            raise AssertionError(f"CRS differs: {rel(p)}")
        if not np.array_equal(old.geometry.to_wkb(), new.geometry.to_wkb()):
            raise AssertionError(f"Geometry WKB differs: {rel(p)}")
        pd.testing.assert_frame_equal(pd.DataFrame(old.drop(columns="geometry")), pd.DataFrame(new.drop(columns="geometry")),
                                      check_dtype=False, atol=1e-12, rtol=1e-12, obj=rel(p))
        geometry_rows[rel(p)] = len(new)
    fig_now = {rel(p): sha256(p) for p in figures}
    report = {
        "result": "PASS semantic replay",
        "first_run_built_at": first["built_at"], "second_run_built_at": man["built_at"],
        "same_implementation_sha256": man["implementation"]["sha256"], "same_config_inputs_actual_runtime": True,
        "runtime": man["runtime"], "both_runs_fresh_by_manifest_status": True,
        "tables_and_metadata_compared": len(tables), "compared_files": [rel(p) for p in tables],
        "max_abs_numeric_difference": max_abs, "tolerance": {"atol": 1e-12, "rtol": 1e-12},
        "gpkg_geometry_rows": geometry_rows,
        "gpkg_byte_identical": {rel(p): sha256(SNAPSHOT / rel(p)) == sha256(p) for p in gis},
        "figures_byte_identical": sorted(k for k, v in fig_now.items() if first["figure_sha256"].get(k) == v),
        "figures_byte_changed": sorted(k for k, v in fig_now.items() if first["figure_sha256"].get(k) != v),
        "boundary": ("Same frozen local candidate inputs only; not raw-to-result, not the consolidated integrated "
                     "candidate, not a fresh environment. Container/figure bytes are informational, not scientific equivalence."),
    }
    write_json(REPORT, report)
    print(json.dumps({k: v for k, v in report.items() if k != "compared_files"}, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--capture", action="store_true")
    args = ap.parse_args()
    try:
        capture() if args.capture else compare()
    except AssertionError as exc:
        if not args.capture:
            write_json(REPORT, {"result": "FAIL", "reason": str(exc)[:4000]})
        print(f"FAIL: {exc}")
        sys.exit(1)
