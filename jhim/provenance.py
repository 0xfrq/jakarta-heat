"""Content identity for the scientific implementation, configuration and saved artifacts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from . import config as C
from .util import sha256

SOURCE_ROOT = Path(__file__).resolve().parents[1]


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def implementation_identity(root=None):
    root = Path(root or SOURCE_ROOT)
    names = [p for folder in ("jhim", "dashboard", "scripts") for p in (root / folder).rglob("*.py")]
    names += [root / n for n in ("docs/model_specification.json", "docs/scenario_registry.csv",
                                 "docs/spatial_inference_spec.md", "requirements.lock", "requirements-agent3.lock")
              if (root / n).exists()]
    files = {p.relative_to(root).as_posix(): sha256(p) for p in sorted(names)}
    return {"sha256": digest(files), "files": files}


def _portable(path, root):
    """Repository-relative POSIX path when possible; identity is the SHA-256."""
    p = Path(path).resolve()
    try:
        return p.relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        return p.as_posix()


def inputs_identity(paths):
    pairs = [("master_grid", paths.grid), ("grid_master_csv", paths.grid_master),
             ("spatial_features", paths.spatial_features), ("population_accessibility_legacy", paths.pop),
             ("remote_sensing", paths.rs), ("demographic_support", paths.demographic_support),
             ("demographic_corrected", paths.demographic_corrected)]
    pairs += [(f"part_{p.stem}", p) for p in paths.pop_parts]
    pairs += [(f"integrated_{name}", paths.processed / name) for name in (
        "agent2_route_scenarios.csv", "integrated_comparisons/input_lineage.json",
        "integrated_comparisons/auditor_raster_support.csv", "integrated_comparisons/auditor_network.csv")]
    pairs += [("aggregation_scenarios", paths.root / "outputs/qa/remediation_agent2/partial_grid_scenarios.csv")]
    pairs += [(f"frozen_{name}", paths.inputs_dir / name) for name in (
        "audited_merged_grid.csv", "audited_priority_models.csv", "auditor_raster_support.csv", "auditor_network.csv", "input_lineage.json")]
    return {k: {"path": _portable(p, paths.root), "exists": p.exists(), "sha256": sha256(p)} for k, p in pairs}


def output_identity(paths):
    # Includes numerical/geometry exports. GPKG byte identity is conservative: a byte change is stale.
    # Keys are checkout-portable repository-relative paths; values remain exact-file SHA-256.
    return {_portable(p, paths.root): sha256(p) for folder in (paths.modeling, paths.tables, paths.figures, paths.gis, paths.tables.parent / "paper")
            if folder.exists() for p in sorted(folder.rglob("*"))
            if p.is_file() and p.name not in ("run_manifest.json", "output_sha256_manifest.csv")}


def scientific_config():
    # JSON roundtrip snapshots mutable dictionaries instead of retaining references to MODELS.
    return json.loads(json.dumps(C.config_snapshot()))


def manifest_status(paths, man, expected_runtime=None):
    stale = []
    if man.get("schema_version") != 2:
        stale.append("manifest_schema_unverified")
    now = inputs_identity(paths)
    old = man.get("inputs", {})
    stale += [k for k in set(now) | set(old) if now.get(k) != old.get(k)]
    if man.get("config") != scientific_config():
        stale.append("scientific_config")
    if man.get("implementation") != implementation_identity():
        stale.append("implementation")
    if man.get("outputs") != output_identity(paths):
        stale.append("output_content")
    if expected_runtime is not None and any(man.get("runtime", {}).get(k) != v for k, v in expected_runtime.items()):
        stale.append("runtime_parameters")
    # If spatial metadata was generated, it must agree with the recorded actual override.
    info = paths.tables / "spatial_validation_info.json"
    if "spatial" in man.get("steps", []) and info.exists():
        if json.loads(info.read_text(encoding="utf-8")).get("permutations") != man.get("runtime", {}).get("permutations"):
            stale.append("runtime_artifact_mismatch")
    return sorted(set(stale))
