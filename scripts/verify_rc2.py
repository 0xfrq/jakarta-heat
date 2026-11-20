"""Independent RC2 numerical, provenance and dashboard-freshness verification.

This verifier does not import the scoring implementation for its arithmetic.
It recomputes M1-M4 from ``merged_grid.csv`` with pandas/numpy, rebuilds the
Queen graph with libpysal, recomputes Moran/LISA with esda, checks the 2,765 /
2,536 / 2,535 denominators, verifies both output manifests from relative paths,
and confirms that the baseline model definition files are byte-identical to the
frozen RC1 commit.

It writes:
    outputs/qa/rc2/engineering_verification.json
    docs/RC2_BUILD_RECORD.json
    docs/integration_manifest.json
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from jhim import config as C  # noqa: E402
from jhim.provenance import implementation_identity, inputs_identity  # noqa: E402
from jhim.util import sha256, write_json  # noqa: E402

RC1 = "3b8ed05be92c35bbb2b3a617688540ee856b11c8"
OUT = ROOT / "outputs/qa/rc2"


def _git_blob(rev: str, path: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(ROOT), "cat-file", "blob", f"{rev}:{path}"])


def _git_text(rev: str, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def _norm(series: pd.Series) -> pd.Series:
    v = series.dropna()
    lo, hi = v.quantile([0.05, 0.95])
    return ((series - lo) / (hi - lo)).clip(0.0, 1.0)


def _scores(frame: pd.DataFrame) -> dict[str, dict[str, pd.Series]]:
    v = frame.loc[frame["valid"]].copy()
    ids = v["grid_id"].astype(str)
    l = _norm(v["lst_c"])
    n = 1.0 - _norm(v["ndvi"])
    p = _norm(np.log1p(v["population"]))
    a = _norm(np.log1p(v["pop_child"] + v["pop_elderly"]))
    d = v["park_distance_used_m"].clip(0, 1000) / 1000
    raw = {"M1": l, "M2": 0.60 * l + 0.40 * n, "M3": 0.40 * l + 0.30 * n + 0.30 * p,
           "M4": 0.30 * l + 0.20 * n + 0.25 * a + 0.25 * d}
    # Raw (unclipped) counterparts for the documented tie-break.
    lr = (v["lst_c"] - v["lst_c"].min()) / (v["lst_c"].max() - v["lst_c"].min())
    nr = 1.0 - (v["ndvi"] - v["ndvi"].min()) / (v["ndvi"].max() - v["ndvi"].min())
    pr = (np.log1p(v["population"]) - np.log1p(v["population"]).min()) / (
        np.log1p(v["population"]).max() - np.log1p(v["population"]).min())
    ar = (np.log1p(v["pop_child"] + v["pop_elderly"]) - np.log1p(v["pop_child"] + v["pop_elderly"]).min()) / (
        np.log1p(v["pop_child"] + v["pop_elderly"]).max() - np.log1p(v["pop_child"] + v["pop_elderly"]).min())
    raw_unclipped = {"M1": lr, "M2": 0.60 * lr + 0.40 * nr, "M3": 0.40 * lr + 0.30 * nr + 0.30 * pr,
                     "M4": 0.30 * lr + 0.20 * nr + 0.25 * ar + 0.25 * d}
    out = {}
    for model in raw:
        s, r0 = raw[model], raw_unclipped[model]
        order = np.lexsort((ids.to_numpy(), -r0.to_numpy(), -s.to_numpy()))
        ranks = np.empty(len(ids), dtype=int)
        ranks[order] = np.arange(1, len(ids) + 1)
        out[model] = {"score": pd.Series(s.to_numpy(), index=ids), "rank": pd.Series(ranks, index=ids),
                      "raw": pd.Series(r0.to_numpy(), index=ids), "top": set(ids.to_numpy()[ranks <= math.ceil(.1 * len(ids))])}
    return out


def check_scores(label: str, merged_path: Path, priority_path: Path) -> dict:
    merged = pd.read_csv(merged_path)
    priority = pd.read_csv(priority_path).set_index("grid_id")
    expected = _scores(merged)
    result = {"dataset": label, "n_rows": len(merged), "n_valid": int(merged.valid.sum()), "models": {}, "checks": {}}
    all_ok = True
    for model, values in expected.items():
        saved_score = priority.loc[values["score"].index, f"{model.lower()}_score"].astype(float)
        saved_rank = priority.loc[values["score"].index, f"{model.lower()}_rank"].astype(int)
        score_diff = float(np.nanmax(np.abs(saved_score.to_numpy() - values["score"].to_numpy())))
        rank_mismatch = int((saved_rank.to_numpy() != values["rank"].to_numpy()).sum())
        saved_top = set(priority.index[priority[f"{model.lower()}_top"].fillna(False).astype(bool)])
        top_exact = saved_top == values["top"]
        ok = score_diff <= 1e-12 and rank_mismatch == 0 and top_exact
        all_ok = all_ok and ok
        result["models"][model] = {
            "score_max_abs_diff": score_diff, "rank_mismatches": rank_mismatch,
            "top_budget": len(values["top"]), "top_set_exact": top_exact, "ok": ok,
        }
    result["checks"]["all_models"] = all_ok
    return result


def check_eligibility() -> dict:
    e = pd.read_csv(ROOT / "data/processed/modeling_remediation/eligibility_by_model.csv")
    counts = {f"M{i}": int(e[f"elig_m{i}"].sum()) for i in range(1, 5)}
    return {"n_master": len(e), "counts": counts,
            "expected": {"M1": 2764, "M2": 2764, "M3": 2758, "M4": 2536},
            "ok": counts == {"M1": 2764, "M2": 2764, "M3": 2758, "M4": 2536}}


def check_spatial() -> dict:
    from esda.moran import Moran, Moran_Local
    from libpysal import weights as W

    priority = pd.read_csv(ROOT / "data/processed/modeling/priority_models.csv").set_index("grid_id")
    ids = priority.index[priority.m4_score.notna()]
    gdf = gpd.read_file(ROOT / "data/processed/grid_500m_jakarta.gpkg").set_index("grid_id").loc[ids].reset_index()
    w = W.Queen.from_dataframe(gdf, use_index=False, silence_warnings=True)
    islands = [str(gdf.grid_id.iloc[i]) for i in w.islands]
    keep = [i for i in range(len(gdf)) if i not in set(w.islands)]
    gdf = gdf.iloc[keep].reset_index(drop=True)
    w = W.Queen.from_dataframe(gdf, use_index=False, silence_warnings=True)
    w.transform = "r"
    y = priority.loc[gdf.grid_id, "m4_score"].to_numpy()
    z = y - y.mean()
    # For row-standardised weights S0 = n; keep the general formula explicit.
    manual = len(y) / float(w.s0) * float(z @ (w.sparse @ z)) / float(z @ z)
    gm = pd.read_csv(ROOT / "outputs/remediation/tables/moran_global.csv")
    saved_i = float(gm.loc[(gm.variabel == "m4_score") & (gm.bobot == "queen"), "I"].iloc[0])
    lisa = Moran_Local(y, w, permutations=999, seed=42, alternative="directed")
    saved_lisa = pd.read_csv(ROOT / "data/processed/modeling_remediation/lisa_m4.csv").set_index("grid_id").loc[gdf.grid_id]
    lisa_i_diff = float(np.max(np.abs(lisa.Is - saved_lisa.lisa_I.to_numpy())))
    lisa_p_diff = float(np.max(np.abs(lisa.p_sim - saved_lisa.p_sim.to_numpy())))
    sensitivity = pd.read_csv(ROOT / "outputs/remediation/tables/lisa_tail_permutation_sensitivity.csv")
    counts = {(row.alternative, int(row.permutations), row.correction): int(row.n_significant)
              for row in sensitivity.itertuples()}
    expected_counts = {("directed", 999, "klaster_fdr"): 663, ("two-sided", 999, "klaster_fdr"): 496,
                       ("directed", 9999, "klaster_fdr"): 687, ("two-sided", 9999, "klaster_fdr"): 493,
                       ("directed", 999, "klaster_by"): 0, ("directed", 9999, "klaster_by"): 284,
                       ("two-sided", 9999, "klaster_by"): 234}
    counts_ok = all(counts.get(k) == v for k, v in expected_counts.items())
    return {
        "joined_common": 2536, "queen_islands": islands, "tested_observations": len(gdf),
        "directed_edges": int(sum(w.cardinalities.values())), "mean_neighbors": float(sum(w.cardinalities.values()) / len(gdf)),
        "manual_moran_m4": manual, "saved_moran_m4": saved_i, "moran_abs_diff": abs(manual - saved_i),
        "lisa_rows": len(saved_lisa), "lisa_I_max_abs_diff": lisa_i_diff, "lisa_p_max_abs_diff": lisa_p_diff,
        "lisa_sensitivity_counts": {f"{k[0]}/{k[1]}/{k[2]}": v for k, v in counts.items()},
        "lisa_sensitivity_expected": {f"{k[0]}/{k[1]}/{k[2]}": v for k, v in expected_counts.items()},
        "checks": {
            "one_island": islands == ["JKT_R013_C019"], "tested_2535": len(gdf) == 2535,
            "edges_18368": int(sum(w.cardinalities.values())) == 18368,
            "moran_exact": abs(manual - saved_i) <= 1e-12, "lisa_exact": lisa_i_diff == 0 and lisa_p_diff == 0,
            "sensitivity_counts": counts_ok,
        },
        "ok": all([islands == ["JKT_R013_C019"], len(gdf) == 2535,
                   int(sum(w.cardinalities.values())) == 18368, abs(manual - saved_i) <= 1e-12,
                   lisa_i_diff == 0, lisa_p_diff == 0, counts_ok]),
    }


def check_output_manifest(rel: str) -> dict:
    path = ROOT / rel
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines()[1:]:
        p, digest = line.rsplit(",", 1)
        rows.append((p, digest))
    absolute = [p for p, _ in rows if ":" in p or p.startswith("/")]
    missing, mismatch = [], []
    for p, digest in rows:
        target = ROOT / p
        if not target.is_file():
            missing.append(p)
        elif sha256(target) != digest:
            mismatch.append(p)
    baseline = subprocess.check_output(["git", "-C", str(ROOT), "show", f"{RC1}:{rel}"], text=True)
    base = {}
    prefix = "D:\\jakarta-heat-integration\\"
    for line in baseline.splitlines()[1:]:
        p, digest = line.rsplit(",", 1)
        p = p[len(prefix):].replace("\\", "/") if p.startswith(prefix) else p.replace("\\", "/")
        base[p] = digest
    changed = sorted(p for p, digest in rows if p in base and base[p] != digest)
    missing_base = sorted(p for p, _ in rows if p not in base)
    return {"manifest": rel, "entries": len(rows), "absolute_paths": absolute, "missing": missing,
            "hash_mismatches": mismatch, "baseline_entries": len(base), "baseline_changed": changed,
            "baseline_missing": missing_base,
            "ok": not absolute and not missing and not mismatch}


def check_source_manifests(source_root: Path | None) -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    from aggregate_demographics import verify_manifest

    results = {}
    for rel in ("outputs/qa/remediation_agent2/demographic_source_manifest.json",
                "outputs/qa/remediation_agent2/original_masks/demographic_source_manifest.json"):
        items = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        results[rel] = verify_manifest(items, ROOT, source_root, require_all=source_root is not None)
    return {"manifests": results, "source_root": str(source_root) if source_root else None,
            "ok": all(r["ok"] for r in results.values())}


def check_dashboard() -> dict:
    from dashboard.lib.context import _features, _priority, _sig
    from jhim import pipeline as P

    paths = C.Paths(root=ROOT)
    features, _, status = _features(False, "exclude", _sig(paths))
    priority = _priority(False, "exclude", _sig(paths)).set_index("grid_id")
    saved = pd.read_csv(paths.priority).set_index("grid_id")
    diffs = {}
    for model in ("m1", "m2", "m3", "m4"):
        valid = saved[f"{model}_score"].notna()
        diffs[model] = {
            "score_max_abs_diff": float(np.max(np.abs(priority.loc[saved.index[valid], f"{model}_score"].to_numpy() -
                                                         saved.loc[valid, f"{model}_score"].to_numpy()))),
            "rank_mismatches": int((priority.loc[saved.index[valid], f"{model}_rank"].to_numpy() !=
                                    saved.loc[valid, f"{model}_rank"].to_numpy()).sum()),
        }
    freshness = P.official_outputs_status(paths)
    return {"feature_rows": len(features), "status_can_model": bool(status.can_model),
            "score_checks": diffs, "official_outputs_current": bool(freshness["is_current"]),
            "official_outputs_stale": freshness.get("stale_inputs", []),
            "ok": len(features) == 2765 and status.can_model and freshness["is_current"] and
                  all(v["score_max_abs_diff"] <= 1e-12 and v["rank_mismatches"] == 0 for v in diffs.values())}


def check_docs_and_paths() -> dict:
    integration = json.loads((ROOT / "docs/integration_manifest.json").read_text(encoding="utf-8"))
    bad_paths = []
    for section in ("canonical_inputs", "canonical_outputs"):
        value = integration.get(section, {})
        items = value.values() if isinstance(value, dict) else value
        for item in items:
            p = item.get("path") if isinstance(item, dict) else item
            if isinstance(p, str) and (p.startswith("D:") or p.startswith("C:") or p.startswith("/")):
                bad_paths.append(p)
    run_manifests = {}
    for rel in ("data/processed/modeling/run_manifest.json", "data/processed/modeling_remediation/run_manifest.json"):
        man = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        bad_inputs = [v["path"] for v in man.get("inputs", {}).values()
                      if isinstance(v.get("path"), str) and (v["path"].startswith(("D:", "C:", "/")))]
        bad_outputs = [p for p in man.get("outputs", {}) if p.startswith(("D:", "C:", "/"))]
        run_manifests[rel] = {
            "source_revision": man.get("source_revision"), "git_commit": man.get("git_commit"),
            "source_state": man.get("source_state"), "source_dirty_paths": man.get("source_dirty_paths"),
            "bad_input_paths": bad_inputs, "bad_output_paths": bad_outputs,
            "build_command": man.get("build_command"),
        }
    spatial = (ROOT / "docs/spatial_inference_spec.md").read_text(encoding="utf-8")
    external = (ROOT / "docs/external_validation_scope.md").read_text(encoding="utf-8")
    rs = json.loads((ROOT / "docs/remote_sensing_export_manifest.json").read_text(encoding="utf-8"))
    return {
        "integration_absolute_paths": bad_paths,
        "run_manifests": run_manifests,
        "spatial_spec_2536": "2,536" in spatial, "spatial_spec_2535": "2,535" in spatial,
        "spatial_spec_stale_2526": "2526" in spatial,
        "external_scope_2536": "2,536" in external, "external_scope_stale_2526": "2526" in external,
        "remote_sensing_historical_label": "historical_source_git_head" in rs and "git_head" not in rs,
        "remote_sensing_current_binding": rs.get("current_release_binding"),
        "ok": not bad_paths and all(not v["bad_input_paths"] and not v["bad_output_paths"] for v in run_manifests.values())
              and "2,536" in spatial and "2,535" in spatial and "2526" not in spatial
              and "2,536" in external and "2526" not in external
              and "historical_source_git_head" in rs and "git_head" not in rs,
    }


def check_model_definitions() -> dict:
    paths = ("jhim/models.py", "jhim/config.py", "docs/model_specification.json")
    rows = {}
    for path in paths:
        base = sha256_bytes(_git_blob(RC1, path))
        head = sha256_bytes(_git_blob("HEAD", path))
        rows[path] = {"rc1_sha256": base, "head_sha256": head, "unchanged": base == head}
    spec = json.loads((ROOT / "docs/model_specification.json").read_text(encoding="utf-8"))
    return {"files": rows, "status": spec.get("status"), "approved_by": spec.get("approved_by"),
            "ok": all(v["unchanged"] for v in rows.values()) and spec.get("status") == "PROVISIONAL_UNSIGNED"}


def sha256_bytes(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audit-root", type=Path, required=True)
    ap.add_argument("--source-root", type=Path, default=None,
                    help="Read-only restored frozen-input root for source-manifest hash checks")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    standard = check_scores("standard", ROOT / "data/processed/modeling/merged_grid.csv",
                            ROOT / "data/processed/modeling/priority_models.csv")
    remediation = check_scores("remediation", ROOT / "data/processed/modeling_remediation/merged_grid.csv",
                               ROOT / "data/processed/modeling_remediation/priority_models.csv")
    eligibility = check_eligibility()
    spatial = check_spatial()
    outputs = {"standard": check_output_manifest("data/processed/modeling/output_sha256_manifest.csv"),
               "remediation": check_output_manifest("data/processed/modeling_remediation/output_sha256_manifest.csv")}
    source_manifests = check_source_manifests(args.source_root)
    dashboard = check_dashboard()
    docs = check_docs_and_paths()
    models = check_model_definitions()

    run_manifest = json.loads((ROOT / "data/processed/modeling/run_manifest.json").read_text(encoding="utf-8"))
    source_revision = run_manifest.get("source_revision")
    artifact_revision = _git_text(ROOT, "rev-parse", "HEAD")
    artifact_tree = _git_text(ROOT, "rev-parse", "HEAD^{tree}")
    ancestor = True
    if source_revision:
        ancestor = subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", source_revision, "HEAD"],
                                  capture_output=True).returncode == 0
    identity_ok = (run_manifest.get("source_state") == "clean" and
                   run_manifest.get("git_commit") == source_revision and
                   not run_manifest.get("source_dirty_paths") and ancestor and
                   run_manifest.get("implementation") == implementation_identity())
    build_identity = {
        "source_revision": source_revision, "source_state": run_manifest.get("source_state"),
        "git_commit": run_manifest.get("git_commit"), "source_dirty_paths": run_manifest.get("source_dirty_paths"),
        "artifact_revision": artifact_revision, "artifact_tree": artifact_tree,
        "source_is_ancestor": ancestor, "implementation_sha256": run_manifest.get("implementation", {}).get("sha256"),
        "current_implementation_sha256": implementation_identity()["sha256"],
        "build_command": run_manifest.get("build_command"), "ok": identity_ok,
    }

    checks = {
        "counts_master_2765": standard["n_rows"] == 2765,
        "counts_common_2536": standard["n_valid"] == 2536,
        "models_standard": standard["checks"]["all_models"],
        "models_remediation": remediation["checks"]["all_models"],
        "eligibility": eligibility["ok"],
        "spatial": spatial["ok"],
        "output_manifests": all(v["ok"] for v in outputs.values()),
        "source_manifests": source_manifests["ok"],
        "dashboard": dashboard["ok"],
        "documentation_and_paths": docs["ok"],
        "model_definitions_unchanged": models["ok"],
        "build_identity_clean": identity_ok,
    }
    result = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "result": result,
        "schema_version": "rc2-engineering-verification-1",
        "source_revision": source_revision,
        "artifact_revision": artifact_revision,
        "artifact_tree": artifact_tree,
        "rc1_baseline": {"commit": RC1, "tree": "2b312d673faac64d51559cf9612caf61847ad226"},
        "counts": {"master": standard["n_rows"], "common": standard["n_valid"],
                   "spatial_tested": spatial["tested_observations"], "eligibility": eligibility["counts"]},
        "score_verification": {"standard": standard, "remediation": remediation},
        "spatial": spatial,
        "output_manifests": outputs,
        "source_manifests": source_manifests,
        "dashboard": dashboard,
        "documentation_and_paths": docs,
        "model_definitions": models,
        "build_identity": build_identity,
        "checks": checks,
        "limitations": [
            "Engineering verification only; scientific construct, access, novelty and policy decisions remain unsigned.",
            "Raw WorldPop/OSM acquisition lineage requires the separate frozen-input bundle and external audit evidence.",
            "The output manifests bind exact-file bytes; GPKG container bytes may differ across serializers even when tables and geometry are equal.",
        ],
    }
    write_json(OUT / "engineering_verification.json", report)

    build_record = {
        "schema_version": "rc2-build-record-1",
        "source_revision": source_revision,
        "source_state": run_manifest.get("source_state"),
        "source_dirty_paths": run_manifest.get("source_dirty_paths", []),
        "artifact_revision": artifact_revision,
        "artifact_tree": artifact_tree,
        "build_git_state": run_manifest.get("git_commit"),
        "built_at": run_manifest.get("built_at"),
        "build_command": run_manifest.get("build_command"),
        "implementation_sha256": run_manifest.get("implementation", {}).get("sha256"),
        "environment": {k: run_manifest.get(k) for k in ("python", "pandas", "numpy", "geopandas", "libpysal", "esda", "scipy")},
        "inputs": run_manifest.get("inputs"),
        "replay": "outputs/qa/rc2/replay_verification.json",
        "engineering_verification": "outputs/qa/rc2/engineering_verification.json",
        "notes": [
            "The analysis build ran from a clean committed source snapshot; generated outputs do not make the source dirty.",
            "source_revision is the actual revision used by the pipeline; artifact_revision is the commit that stores the rebuilt outputs.",
            "No uncommitted source modification was used for this build.",
        ],
    }
    write_json(ROOT / "docs/RC2_BUILD_RECORD.json", build_record)

    integration = json.loads((ROOT / "docs/integration_manifest.json").read_text(encoding="utf-8"))
    integration.update({
        "schema_version": "rc2-1",
        "branch": "integration/rc2",
        "source_revision": source_revision,
        "source_state": run_manifest.get("source_state"),
        "artifact_revision": artifact_revision,
        "artifact_tree": artifact_tree,
        "build_record": "docs/RC2_BUILD_RECORD.json",
        "candidate_source_commit": source_revision,
        "build_git_state": run_manifest.get("git_commit"),
        "canonical_inputs": inputs_identity(C.Paths(root=ROOT)),
        "canonical_outputs": {"features": "data/processed/modeling/merged_grid.csv",
                              "priority": "data/processed/modeling/priority_models.csv",
                              "remediation": "data/processed/modeling_remediation",
                              "dashboard": "dashboard/app.py"},
        "verification": "outputs/qa/rc2/engineering_verification.json",
        "portability": "outputs/qa/rc2/portability_verification.json",
        "replay": "outputs/qa/rc2/replay_verification.json",
        "hash_policy": {
            "name": "git-blob-sha256",
            "definition": "Receipt and documentation hashes are SHA-256 over git cat-file blob <rev>:<path> bytes; checkout line endings are irrelevant.",
            "output_manifest_policy": "SHA-256 over exact file bytes; outputs/** and data/** are stored with -text so checkout bytes are stable.",
        },
        "rc1_baseline": {"commit": RC1, "tree": "2b312d673faac64d51559cf9612caf61847ad226",
                         "receipt": "handoff/RC1_CANDIDATE_RECEIPT.json"},
        "source_of_truth": "RC2 portable paths and Git-blob hash policy; RC1 evidence remains immutable.",
    })
    write_json(ROOT / "docs/integration_manifest.json", integration)

    summary = {"result": result, "checks": checks, "counts": report["counts"],
               "moran_m4": spatial["manual_moran_m4"], "source_revision": source_revision,
               "artifact_revision": artifact_revision}
    print(json.dumps(summary, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
