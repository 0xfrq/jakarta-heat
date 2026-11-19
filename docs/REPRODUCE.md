# Reproducing the Agent 2 remediation outputs (IN-02, Agent 2 scope)

Scope: Agent 2 GIS/demographic/park/walking remediation outputs, rebuilt **offline
from declared frozen inputs**. This is *not* a consolidated raw-to-paper pass:
Agent 1 remote-sensing export and Agent 3 model/dashboard stages are outside this
lane, and consolidated verification remains **NOT YET TESTED** until an IN-01
committed candidate exists.

## 1. Platform and native libraries (actually used)

| Item | Version |
|---|---|
| OS | Windows 11 (10.0.26300), x64 |
| Python | 3.12.10 (python.org build, MSC v.1943) |
| GDAL (rasterio wheel) | 3.12.2 |
| GDAL (pyogrio wheel) | 3.12.4 — wheels bundle separate GDAL copies; both are pinned via the lock |
| PROJ (pyproj) | 9.8.1 |
| GEOS (shapely) | 3.14.1 |
| Key packages | geopandas 1.2.0, pandas 3.1.1, numpy 2.5.5, rasterio 1.5.2, pyogrio 0.13.0, shapely 2.2.0, networkx 3.7, osmnx 2.2.0, exactextract 0.3.0, pytest 9.2.0 |

QGIS is **not** required: demographic aggregation is executed by
`scripts/aggregate_demographics.py` (the historical QGIS hybrid rule is
reimplemented and fractional allocation is a sensitivity). The supported
platform is Windows/Python 3.12; other platforms are untested.

## 2. Environment

```powershell
py -3.12 -m venv .venv/reproduction
.venv/reproduction/Scripts/python -m pip install -r requirements.lock
.venv/reproduction/Scripts/python -m pip check
```

`requirements.lock` is the union of the actually installed Agent 2 and Agent 3
pins (no common-version conflicts). Agent 1 GEE/JS tooling is not included.

## 3. Frozen inputs (offline lane)

`docs/agent2_frozen_inputs.json` (version `Agent2-remediation-v2`) lists 55 inputs
with SHA-256 and size. Raw rasters, OSM XML, GraphML and the Overpass cache are gitignored, so
they travel in a bundle:

| Artifact | Location |
|---|---|
| Bundle | `dist/agent2_frozen_inputs_v2.zip` (218.8 MB, gitignored — transfer out-of-band) |
| Bundle SHA-256 | `3fc027ed47b8fb122f8d5ed3fdc3bec7f306d6a358e99ee0c2e42bb00c011f3a` (`dist/agent2_frozen_inputs_v2.sha256`) |

```powershell
# verify the local input closure
.venv/reproduction/Scripts/python scripts/agent2_freeze_inputs.py
# restore into a checkout: only missing files are written; a differing existing file is refused
.venv/reproduction/Scripts/python scripts/agent2_freeze_inputs.py --restore dist/agent2_frozen_inputs_v2.zip
# create a bundle (refuses to overwrite an existing bundle)
.venv/reproduction/Scripts/python scripts/agent2_freeze_inputs.py --bundle dist/agent2_frozen_inputs_vN.zip
```

`--freeze` writes a **new input version**; run it only intentionally.

Licences: WorldPop CC BY 4.0 (attribution); OpenStreetMap ODbL 1.0 (attribution,
share-alike for derived databases). Official municipal web pages in
`outputs/qa/remediation_agent2/park_source_*.html` are archived as evidence
snapshots; redistribution rights are not asserted — the URLs and hashes are the
citation.

## 4. Offline rebuild

```powershell
.\scripts\run_reproduction.ps1 -Scope Agent2
```

Ordered stages (each must exit 0):

1. `pip check`
2. `agent2_freeze_inputs.py` — all 55 input hashes must match
3. `aggregate_demographics.py` on original age masks → `outputs/qa/remediation_agent2/original_masks/`
4. `aggregate_demographics.py` on 1 km-buffered age rasters → `data/processed/demographic_support.csv`, `demographic_features_corrected.csv`
5. `07_integrate_spatial.py --demographics … --support …` → `spatial_features_corrected.csv`
6. `agent2_park_evidence.py` (offline replay of archived evidence; no HTTP)
7. `agent2_connector_remediation.py` (node/connector permission screen, fixed snap nodes)
8. `agent2_remediation_effects.py` (audited-formula replay, scenarios, corrected feature table/GPKG, per-grid route scenarios, figure)
8b. `agent2_integration_manifest.py` → `docs/integration_manifest.json` (read-only git inspection; IN-01 preparation only)
9. pytest: `tests/test_demographic_support.py tests/test_agent2_remediation.py tests/test_agent2_gis.py tests/test_walking_pipeline.py`

Determinism check between two runs:

```powershell
.venv/reproduction/Scripts/python scripts/agent2_compare_runs.py snapshot dist/repro_runs/runA
# ... second run ...
.venv/reproduction/Scripts/python scripts/agent2_compare_runs.py snapshot dist/repro_runs/runB
.venv/reproduction/Scripts/python scripts/agent2_compare_runs.py compare dist/repro_runs/runA dist/repro_runs/runB --report outputs/qa/remediation_agent2/reproduction_equivalence.csv
```

CSV values/IDs/missingness, JSON (minus run-time keys) and GPKG attributes plus
exact geometry are compared semantically; byte identity is reported separately.
PNG figures are presentation artifacts (hash only).

## 5. Online refresh lane (not part of the offline rebuild)

| Stage | Command | External service |
|---|---|---|
| Buffered WorldPop age retrieval | `scripts/agent2_buffered_age.py` | WorldPop API (`api.worldpop.org/v3/raster`) |
| Official park context pages | `scripts/agent2_park_evidence.py --refresh-evidence` | municipal web sites |
| Historical OSM pilot | `scripts/agent2_historical_pilot.py` | Overpass attic queries — **all 6 requests returned HTTP 406 on 2026-11-19** |
| OSM park cache / walking graph | original `scripts/04_extract_parks.py`, `05_walking_accessibility.py` | Overpass / OSMnx |

A refresh produces new inputs; re-run `--freeze` deliberately and record the new
manifest version. Do not overwrite the archived sources.

## 6. Actual results

All runs: Windows 11, Python 3.12.10, `.venv/reproduction` built from
`requirements.lock`; `pip freeze` of that environment equals the lock exactly
(`outputs/qa/remediation_agent2/logs/fresh_env_pip_freeze.txt`). Logs and JUnit
XML for each run are in `outputs/qa/remediation_agent2/logs/`.

| Check | Result |
|---|---|
| `pip check` | No broken requirements found |
| Agent 2 tests (4 files), final code | **69 passed, 7 subtests passed** (workspace runs 4, 5; clean-room run 2) |
| `run_reproduction.ps1 -Scope Agent2` | exit 0; 5.5–7 min per run |
| Run 4 vs run 5 (workspace, sequential, identical code) | 38/38 outputs semantically equal; 35 byte-identical; 3 GPKG differ only in serialization bytes |
| Run 2 vs run 3 (earlier code, sequential) | 38/38 semantically equal; same 3 GPKG byte differences |
| Workspace run 4 vs clean room | 38/38 semantically equal; 35 byte-identical |
| Clean-room restore | 55/55 hashes verified; repeat restore idempotent; tampered existing file refused (exit 1, file untouched) |
| `-Scope Consolidated` | fails before any stage: "IN-01 candidate incomplete: tests/test_remote_sensing_grid.py absent. Consolidated verification NOT TESTED." |

Clean room = `git archive HEAD` of this branch + the 34 Agent 2 source/test/doc
files (no data, no outputs) + `--restore` of the bundle, executed with the same
fresh interpreter. It revealed two defects that were then fixed: frozen-input v1
lacked the audited baseline copies and TM-02 pilot archive (→ v2), and the
demographic source manifest stored absolute paths (→ project-relative, tested).
Equivalence reports: `outputs/qa/remediation_agent2/reproduction_equivalence.csv`,
`cleanroom_equivalence.csv`.

Key reproduced values (exploratory audited-formula replay, not official model
results): 2765 IDs; 6 total/age no-support nulls (19 age with original masks);
common set 2536 (baseline 2538); fractional study-union conservation |Δ| ≤ 4.7e-5
person; missing routes 226 baseline / 407 conservative; M4 top-10% Jaccard 0.992157
(corrected hybrid), 0.881481 (fractional), 0.895582 (conservative, fixed set),
0.421348 (positive-tag stress, fixed set).

Not covered: Agent 1 GEE export, Agent 3 models/spatial/sensitivity/dashboard,
the online refresh lane, non-Windows platforms. Consolidated reproduction remains
**NOT YET TESTED** (IN-01).
