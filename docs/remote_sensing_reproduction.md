# Remote-sensing remediation replay and external blockers

Run from this repository's root using Python 3.12 and
`requirements-remote-sensing.txt`. No command requires a sibling worktree.
The full source/input/output SHA256 inventory and observed package versions
are in `remote_sensing_export_manifest.json`. This is an RS workstream replay;
it is not an integrated raw-to-paper reproduction or an acquisition-origin PASS.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONIOENCODING='utf-8'
& .venv/Scripts/python.exe -m pip check
& .venv/Scripts/python.exe scripts/02b_aggregate_remote_sensing.py --output-dir data/processed/remote_sensing_remediated
& .venv/Scripts/python.exe scripts/02d_validate_remote_sensing.py --rs-dir data/processed/remote_sensing_remediated --output-dir outputs/qa/agent1_remediation/validation
& .venv/Scripts/python.exe scripts/02e_remote_sensing_remediation.py
& .venv/Scripts/python.exe scripts/02e_remote_sensing_remediation.py --verify
& .venv/Scripts/python.exe -m pytest -q -p no:cacheprovider tests/test_remote_sensing_grid.py tests/test_remote_sensing_remediation.py
node --check scripts/02c_dynamic_world_fractions_gee.js
node --check scripts/02f_export_remote_sensing_provenance_gee.js
```

Do not regenerate the evidence manifest before checking it when validating
unchanged frozen artifacts: `--verify` must detect changed files. Evidence-builder
execution is an explicit new evidence generation step, not a staleness bypass.
The original canonical data remains the audited baseline. Integration should
select the revised table deliberately; include all source changes and nullable
supplementary fields. Existing first-eight-column contract and aliases remain.

## RS-01 authenticated-operator checklist

Local probe on 2026-11-20: `ee.Initialize(project='nodemailer-mailer')` raised
`EEException: Please authorize access to your Earth Engine account ...`.
Both the usual Earth Engine credentials file and gcloud ADC file were absent.
No authentication was initiated, credentials copied, or task submitted. A
header-only `remote_sensing_scene_manifest.csv` means **no recovered records**;
it must never be interpreted as zero source scenes. Twelve monthly rows with
null counts similarly mean unavailable evidence, not zero observations.

1. Authorized operator should first try to retrieve original scene/task records
   and the historical AOI asset version. Archive the task JSON and exact exported
   AOI plus SHA256; do not use file modification time as processing date.
2. If unrecoverable, concatenate `02_remote_sensing_gee.js` and
   `02f_export_remote_sensing_provenance_gee.js`. Save and hash the exact combined
   recipe before execution. This is a **new replay**, not recovery of the old job.
   Operator must archive actual task IDs/status/timestamps/error state separately;
   the recipe-evaluation timestamp is not a task completion timestamp.
3. Run the two image exports and four metadata exports: acquisition inventory
   (both collections), monthly clear support, exact AOI GeoJSON, recipe metadata.
   Save results under a distinct replay folder; keep frozen GeoTIFFs untouched.
4. Capture Landsat product IDs, UTC scene dates, WRS path/row, L2SP flags, source
   product-generation metadata and DW source IDs/algorithm versions if available.
   Verify date bounds and deduplicate IDs. `validate_scene_manifest()` checks dates
   and required fields but intentionally never declares task/AOI linkage verified.
5. Compute the downloaded replay file hashes. Compare thermal arrays with:

   ```powershell
   & .venv/Scripts/python.exe scripts/02e_remote_sensing_remediation.py --compare-landsat data/processed/remote_sensing_replay/jakarta_2024_lst_ndvi_qa.tif
   ```

   This records per-band common-valid differences, changed valid masks and changed
   NaN footprints. It refuses misaligned grids; explicitly review harmonization
   if a new AOI/grid is different. Compare the DW raster with the same
   `compare_rasters()` function. Matching arrays alone does not prove original
   task lineage; a documented matching replay is the alternative evidence path.
6. If any measurements or support change, rebuild into a new output directory,
   rerun independent intersections, and send Agent 3 new versions for fixed-ID,
   fixed-model score/rank/top-set comparisons before replacing an official input.
7. Replace the header-only local inventory only with actual recovered/exported
   scene rows. Keep original versus replay identity explicit in an operator
   manifest and record exact processing times, script/AOI hashes and task links.
   Preserve and version all evidence before rebuilding the local manifest.

The optional DW label script is separate: a new export uses explicit lowest-code
ties and the frozen 10 m affine transform. It is supplementary, has not run on
GEE, and cannot close a categorical-area claim without actual intersections.

Coordinator decisions still required: temporal estimand/claim scope (TM-01),
primary support and uncertainty policy (RS-02), and defer versus complete R3
(DW-01). No sign-off is inferred from passing tests.
