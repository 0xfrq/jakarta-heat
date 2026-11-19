# Agent 2 remediation ledger

Updated: 20 November 2026 WIB (continuation session after the checkpoint hand-over).
Workspace `D:/jakarta-heat-agent2`, role Agent 2. Auditor documents at
`D:/jakarta-heat/audit` were read and not modified. No commit, push, reset, clean,
merge, or write into another worktree was performed; other worktrees were only
inspected with `git --no-optional-locks status`. This ledger is **not** an
independent closure: every row in the auditor's acceptance matrix stays OPEN
until independent re-audit (QA-01). Seven owned issues, all P1; the register
contains no proven P0.

| Issue | Agent 2 status | Why not closed |
|---|---|---|
| DM-01 | **Implementation complete; ready for independent verification** | Agent 3 DM-02 must adopt; auditor must replay mask diagnosis |
| AC-01 | PARTIAL | No verified public opening/entrance evidence; primary destination construct unsigned |
| AC-02 | PARTIAL | Physical/legal crossings, gates, conditional access unverified; permission policy unsigned |
| BG-01 | PARTIAL (analysis complete) | Primary allocation, coverage threshold, count vs density need coordinator decision |
| TM-02 | BLOCKED for historical claims | All 6 historical requests HTTP 406; deferral needs signed TM-01 mixed-period scope |
| IN-02 | PARTIAL (Agent 2 lane PASS locally) | Consolidated A1/A2/A3 rebuild depends on IN-01 |
| IN-01 | BLOCKED | No commit authorization / committed consolidated candidate |

## Verified execution in this session

All commands ran in the fresh environment `.venv/reproduction` (installed from
`requirements.lock`). Logs: `outputs/qa/remediation_agent2/logs/`.

- `pip check`: **No broken requirements found.**
- Full Agent 2 suite (`tests/test_demographic_support.py tests/test_agent2_remediation.py tests/test_agent2_gis.py tests/test_walking_pipeline.py`):
  first run **1 failed, 65 passed** — a real defect (see DM-01: support-area
  fraction 1+7.6e-12 at `JKT_R052_C000`). After the fix: **66 passed + 7 subtests**;
  after adding interface/portability tests: **69 passed + 7 subtests** (final code,
  workspace run 4/5 and clean-room run 2). JUnit XML retained per run.
- `scripts/run_reproduction.ps1 -Scope Agent2` executed end-to-end 5× in the
  workspace and 2× in a clean room (≈5.5–7 min each).
- Determinism (`scripts/agent2_compare_runs.py`, semantic = CSV values/IDs/
  missingness, JSON minus run-time keys, GPKG attributes + exact geometry):
  - run 2 vs run 3 (sequential): **38/38 semantically equal**, 35 byte-identical;
    the 3 byte differences are GPKG serialization only.
    `outputs/qa/remediation_agent2/reproduction_equivalence.csv`.
  - workspace run 4 vs clean-room run (git `HEAD` archive + Agent 2 sources +
    restored frozen bundle, no other data): **38/38 equal**, 35 byte-identical.
    `outputs/qa/remediation_agent2/cleanroom_equivalence.csv`.
  - run 4 vs run 5 (sequential, identical final code): **38/38 equal**, 35
    byte-identical (same 3 GPKG). `pip freeze` of the fresh env equals the lock.
- Clean-room restore found two genuine closure gaps in frozen-input v1 (audited
  baseline copies `outputs/qa/agent2/baseline/person2/*.csv` and the TM-02 pilot
  archive). Fixed in **v2: 55 inputs**, bundle `dist/agent2_frozen_inputs_v2.zip`
  (SHA-256 `3fc027ed47b8fb122f8d5ed3fdc3bec7f306d6a358e99ee0c2e42bb00c011f3a`).
  It also exposed absolute paths in `demographic_source_manifest.json`; now
  project-relative with a regression test.
- Restore safety: second restore is idempotent; a tampered existing file is
  refused (`ValueError: Refuse overwrite`, file untouched).
- `-Scope Consolidated` fails before any stage: "IN-01 candidate incomplete:
  tests/test_remote_sensing_grid.py absent. Consolidated verification NOT TESTED."
- Park evidence replay is offline: no HTTP without `--refresh-evidence`; archived
  snapshot hashes retained; unsupported Taman Walang publication date is now blank.
- Figures inspected visually: `disputed_connectors.png` (readable; red = explicit
  node conflict, orange = review, green = candidate parks) and
  `demographic_aggregation_priority_changes.png` (overlapping titles fixed; panels
  now state 1/1 and 16/16 entrants/leavers).

## DM-01 — P1 — implementation complete, awaiting independent verification

**Root cause:** 19 age and 6 total-population empty-mask sums exported as 0;
unbuffered age API polygon masking removed valid edge pixel centres. No evidence
of national age-product failure.

**Correction:** real 2024 WorldPop R2025A age rasters with 1 km buffer (identical
on all 74,429 formerly valid pixels per raster, no valid pixel lost, identical
source tags). 13 age gaps recovered from actual source pixels; 6 cells without
any total/age support are analytical null with raw zeros kept in `*_raw`.
Supported estimated zeros (e.g. `JKT_R050_C061`) remain 0 with state
`valid_estimated_zero`. Support area is now clipped to the UTM polygon with an
explicit guard (fails if excess >1e-9 relative); only GEOS rounding is clipped.

**Interface (new this session):** `demographic_support.csv` carries
`support_version` (`agent2-DM-01-v1-buffered-age`; original-mask variant
`…-original-masks`), Boolean `qa_population_source_no_support` and
`qa_age_source_no_support` — exactly the fields Agent 3's `attach_demographic_evidence`
requires; `demographic_features_corrected.csv` carries the same `support_version`.
Values unchanged versus previous outputs (verified column by column).

**Acceptance evidence:** 2765 unique IDs in all four corrected tables; all 19/6
reconciled (`demographic_support_reconciliation.csv`); nulls propagate through
spatial/final tables; independent exactextract sums agree (max 5.1e-5 person);
study-union conservation within 0.01 person (actual ≤4.7e-5); join contract
accepts only documented nulls; legacy files byte-identical to audited baseline.

**Effect (exploratory audited-formula replay, not official):** common set 2538 →
2536; child +215.59, elderly +45.54 people; M4 top-10% Jaccard 0.992157
(`JKT_R039_C051` leaves, `JKT_R056_C043` enters); fixed common set retains 254/254.

**Dependency/decision:** Agent 3 DM-02 must consume and regenerate official
outputs; shared vs model-specific eligibility is a coordinator/Agent 3 decision.

## AC-01 — P1 — PARTIAL

All 1015 candidates have an evidence state and full raw tags
(`data/processed/park_access_evidence.csv`): 980 unknown, 28 conditional, 7 positive
tag (unverified). 0 verified public access, 0 verified entrances
(`validated_park_entrances.gpkg` intentionally empty). Auditor top-20 parks all
explicitly unresolved; they cover 91/254 baseline top-M4 origins. Four municipal
pages are archived as context only. Nearest two distinct candidates computed;
2526 origins have a second candidate. Positive-tag-only stress (10 destinations):
2482 distances saturate at 1 km, fixed-set M4 top-10% Jaccard 0.421348 — a
destination-coverage stress, not ground truth. Per-grid stress distances are now in
`data/processed/agent2_route_scenarios.csv`.
**Outstanding:** dated physical-entrance/opening evidence for influential parks.
**Decision:** broad candidate proxy vs validated public construct; until signed,
use qualified proxy language only.

## AC-02 — P1 — PARTIAL

Explicit permission precedence (foot/access), conditional and barrier-only nodes
kept as unknown, snap nodes fixed, no resnapping. 167 origin and 78 park connectors
touch explicitly forbidden nodes; conservative scenario removes 24,370 directed
edges. Missing routes 226 → 407 (no extra from connector screening beyond the node
scenario); no route shortens. Corrected-demographic common set 2355; fixed-set M4
top-10% Jaccard 0.895582. 25,882 barrier-only and 530 conditional nodes remain
explicit uncertainty. Per-grid route versions (baseline, full extent, positive-tag
stress, node-conservative, node+connector-conservative) with policy labels,
`metric_label` (observed vs `no_route_under_scenario_unknown_not_zero`) and source
SHA-256 are exported for Agent 3 joint replay.
**Outstanding:** targeted field/imagery verification of physical crossings and
gates. **Decision:** permission hierarchy, conditional treatment, connector
evidence standard.

## BG-01 — P1 — PARTIAL (analysis complete)

All 383 partial cells and 65 cells with coverage <10% retained. Fractional
allocation conserves study-union totals (above); hybrid differs by ≈±26–30 people
citywide (non-additive by construction). Predeclared coverage thresholds 0/0.1/
0.25/0.5 and a density objective were run on fixed and changing universes with
exact IDs (`partial_grid_scenarios.csv`, `changed_priority_grids.csv`). M4 top-10%:
fractional Jaccard 0.881481 (16 swaps); coverage ≥0.1 → 2492 eligible, 0.961089
changing / 1.0 fixed; density 0.902622 changing. Figure regenerated and inspected.
**Decision:** primary allocation, coverage threshold, count vs density (MD-01).

## TM-02 — P1 — BLOCKED for historical claims

Bounded pilot (3 km squares at Walang/Intirub/Kalijodo; 2024-12-31 vs 2026-11-19,
identical predicates) — all 6 actual requests HTTP 406; request/response archives
are now part of the frozen inputs. Temporal effect is **unknown, not zero**; no
stability claim. Agent 2 documents withdraw actual-2024 access claims
(`docs/agent2_variable_reference_periods.csv`). Can be closed as not required only
after the coordinator signs a TM-01 mixed-period scope and dependent claims are
removed. Do not repeat identical requests without a changed endpoint.

## IN-02 — P1 — PARTIAL (Agent 2 lane passes locally)

Delivered: `requirements.lock`; `scripts/run_reproduction.ps1` (Agent2 /
Consolidated scopes); `scripts/agent2_freeze_inputs.py` (freeze/check/bundle/
restore); `scripts/agent2_compare_runs.py`; `docs/agent2_frozen_inputs.json` v2;
`docs/REPRODUCE.md` (platform, native GDAL/PROJ/GEOS versions, offline vs online
lanes, licences, commands, actual results). No QGIS clicks and no sibling paths are
required. **Not satisfied:** combined RS/GIS/model tests and a consolidated
raw-to-paper rebuild (depends on IN-01, Agent 1 RS-01 export provenance and
Agent 3 pipeline). Bundle is gitignored and must be transferred out-of-band.

## IN-01 — P1 — BLOCKED

Prepared `docs/integration_manifest.json` (generated by
`scripts/agent2_integration_manifest.py` in every reproduction run): HEAD SHAs and
dirty inventories of all four worktrees (main clean except `audit/`; A1 at
`cdda424`, 21 dirty entries; A2/A3 at `f9b5c02`, A3 51 dirty entries including the
dashboard rename), Agent 2 source hashes, canonical corrected paths with hashes,
preserved legacy outputs, frozen-input availability, and an interface checklist
(nullable support READY; README conflict, dashboard rename, RS aliases PENDING
integrator/A1/A3). Caveat found at commit review: the frozen Agent 3 `jhim` copy
under `outputs/qa/agent2/baseline/agent3/jhim/` is still imported via `sys.path` by
the legacy pre-audit stage `scripts/agent2_gis.py` `integration()`; the remediation
lane and tests never call it, but the integrator must not ship it as importable code. **Blocker:** no authorization to commit/merge; A1/A3 final
owned changes, DM-02 and scientific decisions pending. Consolidated tests remain
**NOT YET TESTED**; nothing was copied into or from Agent 3 code.

## Cross-team notes

DM-02, MD-01/02/03, EL-01, RS-02, ST-01, NV-01/02, IN-03, UI-01 and QA-01 depend
on these outputs; Agent 2 changed none of their code. `JKT_R037_C062` has delivered
LST/NDVI; its exclusion is a 50% thermal-coverage modeling decision, not missing
RS delivery. Agent 3 already has its own `docs/scenario_registry.csv` and
`docs/variable_reference_periods.csv`; Agent 2 supplies compatible
`docs/agent2_scenario_registry.csv` and `docs/agent2_variable_reference_periods.csv`.

## Human decisions required

1. Commit/integration authorization and integrator designation (IN-01).
2. TM-01 temporal scope (mixed 2024 raster / 2026 OSM proxy).
3. AC-01 primary destination construct.
4. AC-02 permission hierarchy, conditional access, connector evidence standard.
5. BG-01 primary allocation, coverage threshold, count vs density.
6. DM-01/DM-02 shared vs model-specific eligibility and adoption of corrected demographics.
