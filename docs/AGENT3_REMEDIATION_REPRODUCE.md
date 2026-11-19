# Reproduce Agent 3 remediation only

Run from this worktree with Python 3.12.10 and its `.venv`. `requirements-agent3.lock` records installed versions; no fresh integrated environment is claimed. This command is an offline analysis from previously prepared/frozen real data, **not raw-to-result reproduction**:

```powershell
.venv/Scripts/python.exe scripts/run_agent3_remediation.py --audit D:\jakarta-heat\audit
.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider tests/agent3
.venv/Scripts/python.exe scripts/verify_agent3_remediation.py
```

Two-run semantic replay (same source/config/inputs/runtime; writes `outputs/remediation/qa/replay_verification.json`):

```powershell
.venv/Scripts/python.exe scripts/check_agent3_replay.py --capture   # after a complete fresh run
.venv/Scripts/python.exe scripts/run_agent3_remediation.py --audit D:\jakarta-heat\audit
.venv/Scripts/python.exe scripts/check_agent3_replay.py             # refuses self-comparison or changed identity
.venv/Scripts/python.exe scripts/check_agent3_dashboard.py          # local browser check, 8 routes + interactions
```

The runner reads only this worktree and read-only auditor evidence. It freezes local audited merged/priority/spatial features and auditor raster support/network into `data/processed/remediation_inputs`. Existing frozen files are checked against their originals; mismatches require a new versioned input path. A local derived RS CSV copies measured values from the audited merged table because the canonical Agent 1 export is absent locally. This is explicitly not new RS acquisition or provenance completion. `input_lineage.json` records original/copy hashes and derivation. Canonical source recovery and export lineage remain DM-01/RS-01 dependencies.

Candidate: `data/processed/modeling_remediation` and `outputs/remediation/{tables,figures,gis,paper,qa}`. Original baseline directories are preserved. The candidate manifest records actual R=999 global/baseline and R=9999 local sensitivities, seed, explicit tails, code-file hashes, config, selected inputs/fallbacks, frozen evidence, local environment lock and output hashes. GPKG byte changes conservatively invalidate freshness; numeric/geometry equivalence is checked separately for replay. `--skip-spatial` is a clearly incomplete development run, not a final result.

Preview the corrected candidate inputs in the dashboard without changing original data:

```powershell
$env:JHIM_INPUT_DIR = "$PWD/data/processed/remediation_inputs"
$env:JHIM_DEMOGRAPHIC_SUPPORT = "$PWD/data/processed/remediation_inputs/demographic_support.csv"
Remove-Item Env:JHIM_RS_PATH -ErrorAction SilentlyContinue
.venv/Scripts/python.exe -m streamlit run dashboard/app.py --server.headless true
```

All eight pages recompute from the same `jhim` implementation, with a mixed-period/candidate-access/support banner and synthetic demo label. Historical saved outputs may correctly appear stale. Clear task-specific variables for normal no-RS mode. Final desktop/narrow interactions must still be repeated on the eventual consolidated candidate; this workstream cannot certify that candidate before it exists.

Integration owner needs A1 canonical RS/export provenance, A2 nullable support/corrected demographics and per-grid access/connector/aggregation versions, the source changes here, approved scientific policy and one clean candidate. No commit, merge, publish or push is performed by this sprint.
