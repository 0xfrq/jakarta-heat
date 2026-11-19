# RC1 consolidated reproduction

Run from the candidate root on Windows x64 / Python 3.12.10. The complete
offline lane uses actual frozen exported rasters, WorldPop masks, the OSM XML,
GraphML and archived comparison tables. It does not reauthenticate to GEE or
redownload OSM/WorldPop. Acquisition-origin lineage remains a separate audit item.

```powershell
python -m venv .venv/rc1
.venv/rc1/Scripts/python.exe -m pip install -r requirements.lock
.venv/rc1/Scripts/python.exe scripts/rc1_restore_inputs.py
.venv/rc1/Scripts/python.exe scripts/run_rc1.py
.venv/rc1/Scripts/python.exe scripts/verify_rc1.py
```

Supply `dist/agent2_frozen_inputs_v2.zip` and its `.sha256` before restore.
The two Agent 1 exports belong under `data/processed/remote_sensing/`;
`docs/remote_sensing_export_manifest.json` records their required hashes.
The bootstrap transfer copied these files from the source worktrees read-only;
runtime rebuilds use only candidate-local inputs and the read-only local audit.
The bundle and rasters are large, so distribute them separately from Git and
verify hashes before using them. `rc1_restore_inputs.py` preserves checkout
originals under `dist/checkout_originals` before any newline-only reconciliation;
non-newline differences fail.

`scripts/run_reproduction.ps1 -Python .venv/rc1/Scripts/python.exe -Scope Consolidated`
calls the same consolidated runner. Stages can be selected explicitly using
`--stage upstream`, `analysis`, `tests`, or `browser`. Each stage writes command,
exit code, timestamp and full logs under `outputs/qa/rc1/`. A nonzero result stops
the runner. Re-run dependent stages after fixing failures; retain their explanation
in the verification document.

Canonical analytical inputs:

| Input | Path / policy |
|---|---|
| Grid / boundary | `data/processed/grid_500m_jakarta.gpkg`, `jakarta_5kota.gpkg`, `grid_master.csv` |
| Remote sensing | `data/processed/remote_sensing_remediated/remote_sensing_grid.csv` |
| Population / ages | `data/processed/demographic_features_corrected.csv` |
| Support | `data/processed/demographic_support.csv`, version `agent2-DM-01-v1-buffered-age` |
| Route baseline | `data/processed/spatial_features.csv`; observed distances remain nullable |
| Route alternatives | `data/processed/agent2_route_scenarios.csv`, five explicit scenarios |
| Fractional allocation | `outputs/qa/remediation_agent2/partial_grid_scenarios.csv`, corrected buffered rasters |

The loader preserves both `raw_*` and `*_raw`, overlays corrected estimates and
support by exact grid ID, and selects Agent 1's remediated output by default.
The legacy RS table and Agent 3 `remediation_inputs/` remain historical comparisons;
the integrated remediation runner cannot silently select them. Standard models,
dashboard caches and remediation models use the same canonical paths. Demo files
and outputs remain separate, and demographic environment overrides cannot affect
demo mode.

Standard outputs are `data/processed/modeling` and `outputs/{tables,figures,gis}`.
Expanded attribution, selection, LISA and route-policy sensitivity outputs are
`data/processed/modeling_remediation` and `outputs/remediation`.
Two full expanded runs are compared semantically, including every table,
selected IDs, labels and GPKG attributes/geometries. Build timestamps and GPKG
container byte variability are distinguished from scientific equivalence.

`verify_rc1.py` independently checks all four equations, tie-breaking/ranks,
top budgets, support propagation, canonical values, dashboard/model equality,
GIS geometries, Shapley sums, BH/BY and matrix-form Moran I. It verifies original
audit hashes and unchanged source refs, then writes the current integration manifest.
Run it again after final commits to verify source/content freshness.

Historical `handoff/REMEDIATION_AGENT*.md`, `docs/AGENT3_REMEDIATION_REPRODUCE.md`
and `docs/agent2_preintegration_manifest.json` describe their original workstream
snapshots. The RC1 handoff, verification and `docs/integration_manifest.json`
describe this candidate. Scientific decisions remain provisional; software
verification does not sign them or close the independent issue register.
