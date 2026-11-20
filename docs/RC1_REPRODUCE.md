# RC1 consolidated reproduction

Run from the candidate root on Windows x64 / Python 3.12.10. The complete
offline lane uses actual frozen exported rasters, WorldPop masks, the OSM XML,
GraphML and archived comparison tables. It does not reauthenticate to GEE or
redownload OSM/WorldPop. Acquisition-origin lineage remains a separate audit item.

```powershell
python -m venv .venv/rc1
.venv/rc1/Scripts/python.exe -m pip install -r requirements.lock
.venv/rc1/Scripts/python.exe -m playwright install chromium
.venv/rc1/Scripts/python.exe scripts/rc1_restore_inputs.py
.venv/rc1/Scripts/python.exe scripts/run_rc1.py --stage upstream   # only when upstream inputs change
.venv/rc1/Scripts/python.exe scripts/run_rc1.py --stage analysis
.venv/rc1/Scripts/python.exe scripts/run_rc1.py --stage tests
.venv/rc1/Scripts/python.exe scripts/run_rc1.py --stage browser
.venv/rc1/Scripts/python.exe scripts/run_rc1.py --stage verify
.venv/rc1/Scripts/python.exe outputs/qa/rc1/check_postbuild_dashboard.py.txt
.venv/rc1/Scripts/python.exe outputs/qa/rc1/verify_release_evidence.py.txt
```

Running `scripts/run_rc1.py` without `--stage` performs upstream, analysis,
tests, browser and verify in that fixed sequential order. Stages may be selected
individually to avoid rerunning unchanged work; rerun every dependent stage after
a source change. The final validated sequence used source build commit
`f1e69a370f743985977e3d90c59179c76eea35d9`. The final artifact commit is later
and is reported separately; do not infer one commit from the other.

Supply `dist/agent2_frozen_inputs_v2.zip` and its `.sha256` before restore.
The two Agent 1 exports belong under `data/processed/remote_sensing/`;
`docs/remote_sensing_export_manifest.json` records their required hashes.
The bootstrap transfer copied these files from the source worktrees read-only;
runtime rebuilds use only candidate-local inputs and the read-only local audit.
The Agent 1 GeoTIFFs are tracked in this candidate; the large Agent 2 bundle is
distributed separately from Git. Verify hashes before using them.
`rc1_restore_inputs.py` preserves checkout
originals under `dist/checkout_originals` before any newline-only reconciliation;
non-newline differences fail.

`scripts/run_reproduction.ps1 -Python .venv/rc1/Scripts/python.exe -Scope Consolidated`
calls the same consolidated runner. Stages can be selected explicitly using
`--stage upstream`, `analysis`, `tests`, `browser`, `verify` or `all`. Each stage
writes command, exit code, timestamp and full logs under `outputs/qa/rc1/`. A
nonzero result stops the runner. The verifier's arithmetic PASS report is
`outputs/qa/rc1/verification.json`; the runner receipt for that stage is the
separate `outputs/qa/rc1/verification_command.json`, so entrypoint-driven
reproduction cannot overwrite the report. Re-run dependent stages after fixing
failures; retain their explanation in the verification document.

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

For continuity, joint-scenario names ending `_legacy` retain Agent 3's naming;
in the integrated run they use the current corrected hybrid reference, while
`_fractional` uses corrected buffered A2 fractional estimates. Original audited
values are separate comparison inputs, not those scenario reference counts.

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
audit hashes and unchanged source refs, then writes the current integration
manifest and the PASS report at `outputs/qa/rc1/verification.json`. The final run
observed 2,765 master grids, 2,536 common eligible grids, 6 age/count-unsupported
cells and manual Moran M4 `0.593024953816681`. Run it again after final commits to
verify source/content freshness. If implementation files changed, rerun the
analysis/replay stages first; do not merely refresh hashes.

`outputs/qa/rc1/verify_release_evidence.py.txt` is the final gate. Its PASS report
is `outputs/qa/rc1/release_evidence_verification.json`; it requires zero
test failures/errors/skips, the executed canonical-A1 contract test, 8 browser
routes/6 interactions/254-row download, post-build freshness, 66 pinned packages,
the independent PASS report, final replay with max difference `0.0`, and matching
implementation/output/frozen-input hashes. The final run reports 236 tests plus
7 subtests, zero skips, 63 replayed tables and implementation SHA
`6b2eae9dc37b14d92bd6accafda602da1e42af643ba8a72b6431d60e985b233e`.
The suite's tested implementation is identical to both final pipeline manifests;
`changed_since_full_suite` is empty.

Historical `handoff/REMEDIATION_AGENT*.md`, `docs/AGENT3_REMEDIATION_REPRODUCE.md`
and `docs/agent2_preintegration_manifest.json` describe their original workstream
snapshots. The RC1 handoff, verification and `docs/integration_manifest.json`
describe this candidate. Scientific decisions remain provisional; software
verification does not sign them or close the independent issue register.
