# Remediation Agent 3 — final workstream ledger (implementer status, not auditor closure)

Date: 20 November 2026 WIB. Workspace `D:\jakarta-heat-agent3`, branch `agent/person3`, base HEAD
`f9b5c02ae2782ca00edcc077a29999b7ada3b91b`. **No commit, push, merge or publish performed or authorized.**
This ledger supersedes the interim version written before the transfer to the replacement agent. "PASS" below is an
implementer statement about this local workstream; independent closure belongs to the auditor
(`D:\jakarta-heat\audit`, read-only, register not edited). Nothing here is a paper-release claim.

Assigned (all P1, no assigned P0): **DM-02, MD-02, MD-03, EL-01, RS-02, ST-01, NV-02, IN-03, UI-01**.
Dependencies outside Agent 3: DM-01 (A2), AC-01/02 (A2), BG-01 (A2), RS-01 (A1), TM-01/02, MD-01, NV-01, QA-01
(coordinator), IN-01/02 (integration owner).

## 1. Final evidence (this session, final source)

| Evidence | Path | Result |
|---|---|---|
| Full test suite | `outputs/remediation/qa/pytest_final.log`, `.xml` | **116 passed, 1 skipped, 1 warning** (178 s). Skip: canonical Agent 1 `remote_sensing_grid.csv` absent locally. Warning: intentional missing-CRS fixture. (Earlier interim run: 111/1/1; earlier same-day rerun before this session's edits: 112/1/1.) |
| Dependency check | `outputs/remediation/qa/pip_check_final.log` | No broken requirements |
| Candidate run 1 / run 2 | `outputs/remediation/qa/final_run1.log`, `final_run2.log` | exit 0 each (~1.9 min); built_at `2026-11-19T19:26:57Z` / `2026-11-19T19:30:18Z` (UTC) |
| Two-run replay | `outputs/remediation/qa/replay_verification.json`, `replay_compare.log` | **PASS semantic replay**: same implementation sha256 `2f122bd9…b163`, config, inputs and actual runtime (R=999, high R=9999, seed 42, directed, top 10%); both manifests fresh; 63 CSV/JSON tables compared, max abs numeric difference **0.0** (tolerance 1e-12); GPKG 2765 rows WKB-identical; 16/16 figures byte-identical; GPKG container bytes differ (build metadata) — informational only |
| Independent verification | `outputs/remediation/qa/independent_verification.json` | PASS within local frozen candidate: decomposition error 2.498e-16, Shapley efficiency 2.274e-13, manual M4 Queen Moran I 0.5921406953903985, support nulls, GIS/table agreement, SciPy BH/BY, frozen input hashes, baseline byte preservation |
| Manifest freshness | `data/processed/modeling_remediation/run_manifest.json` | schema 2, `manifest_status` empty (fresh) after run 2 |
| Dashboard browser | `outputs/remediation/qa/dashboard/browser_check.json`, `../browser_check_final.log` | 8/8 routes, 0 exceptions/page errors, mixed periods + n=2526 visible on 8/8; 6/6 interactions OK (two-sided, BY, uncorrected, custom weights, DEMO label, return to real) |
| Dashboard scope check | `outputs/qa/dashboard_scientific_scope_check.md` | local workstream only, not integrated candidate |

Commands (PowerShell, repo root):

```powershell
.venv/Scripts/python.exe scripts/run_agent3_remediation.py --audit D:\jakarta-heat\audit *> outputs/remediation/qa/final_run1.log
.venv/Scripts/python.exe scripts/check_agent3_replay.py --capture
.venv/Scripts/python.exe scripts/run_agent3_remediation.py --audit D:\jakarta-heat\audit *> outputs/remediation/qa/final_run2.log
.venv/Scripts/python.exe scripts/check_agent3_replay.py
.venv/Scripts/python.exe scripts/verify_agent3_remediation.py
.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider tests/agent3 --junitxml=outputs/remediation/qa/pytest_final.xml *> outputs/remediation/qa/pytest_final.log
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe scripts/check_agent3_dashboard.py
```

## 2. Changes made in this session (replacement agent)

1. **Figures** (`jhim/remediation.py::figures`), found by visual inspection of every PNG:
   - eligibility map: the 12 demographic-only and 1 thermal-QA cells were invisible (clipped coastal/edge slivers) and
     overlapping reasons were silently shown as "route unknown". Now categories with counts — eligible 2526, route
     unknown 219, demographic unsupported 12, thermal QA 1, **multiple reasons 7** — plus location markers for rare
     categories; total 2765 reconciles.
   - city labels used opaque boxes that hid priority cells; now halo text.
   - annotated cases: labels covered city names; colour scale ±2000 vs data range −1061…+472; no colour-bar label.
     Now margin labels with leader lines and rank deltas, horizontal labelled colour bar, data-driven range.
   - **case selection changed** from "8 largest absolute shifts" (which were all losses because the distribution is
     asymmetric) to 4 largest gains + 4 largest losses, ties by grid ID, column `case_selection`
     (`docs/external_validation_scope.md` updated).
   - footer overlapped the x-axis label (count-vs-composition); now placed below the axes. Titles carry n/budgets.
   - `figure_manifest.csv`: absolute Windows paths and collective names (`m1/m2/m3_model_specific/common_eligibility.csv`)
     replaced by repository-relative paths, an explicit `;`-list of every real source file (tables + grid + boundary)
     and each file's SHA-256. Fixed SVG hash salt and no SVG date → byte-stable figures.
2. **Replay helper** (`scripts/check_agent3_replay.py`) hardened before use: requires fresh complete manifests for both
   runs, rejects self-comparison (same `built_at`), compares recorded implementation/config/inputs/runtime of both
   runs, requires identical file sets, includes JSON metadata (only `built_at` ignored) and the paper manifest, all
   GPKGs, figure byte report, writes a FAIL report on failure.
3. **Dashboard** (`dashboard/views/spatial_stats.py`): LISA legend merged "not significant" and "not tested" into
   one state (2765). Now "tidak signifikan (diuji)" vs "tidak diuji (tidak layak / island)", caption with
   significant/tested/untested counts, cross-tab against the *selected* correction, and an explicit note when BH/BY
   yields zero because of permutation resolution.
4. **Browser checker** (`scripts/check_agent3_dashboard.py`): waits for a stable rendered page (previous spatial
   screenshot was half-rendered), full-content-height screenshots (Streamlit scrolls inside `stMain`, so earlier
   screenshots were viewport-only), collapses the sidebar at 390 px (earlier narrow screenshot showed the overlay mid
   transition), adds page 6, real interactions, and fails on interaction errors.
5. **Tests added** (`tests/agent3`): figure-manifest source files exist and re-hash; geographic cases balanced and
   reconcile to attribution; replay helper rejects self-comparison and runtime mismatch; AppTest of all six LISA
   tail × correction combinations including the untested/resolution messages.

## 3. Per-issue ledger

### DM-02 — P1 — Propagate demographic support — **PARTIAL** (local implementation PASS; canonical source pending)

- Original finding: support flags dropped at ingestion; exported age 0 treated as certain; zero-denominator share = 0.
- Root cause: loader consumed `spatial_features.csv` without A2 support fields; structural checks only.
- Files: `jhim/{config,data,pipeline}.py`, `tests/agent3/{test_remediation,test_data_contract,test_models,conftest}.py`,
  `docs/demographic_model_interface.md`, candidate `data/processed/modeling_remediation/*`, dashboard shared banner.
- Correction: versioned full-ID support overlay (`audit-2026-11-20-fractional-mask-v1-PROVISIONAL`), raw exports kept
  as `raw_*`, unsupported analytical counts null, strict Boolean/ID/version validation, zero/missing population →
  undefined composition (NaN), per-model eligibility with overlapping reason codes.
- Tests: suite above; `test_unsupported_zeros_propagate…`, `test_support_contract_failures…`,
  `test_real_support_selection_and_bounds_reconcile`; independent verification "support null propagation".
- Effect: 2765 IDs retained; 19 age-unsupported (6 also total-unsupported) null; shared set 2538→2526; top-10% budget
  254→253; M3/M4 retain 252 baseline top cells (J=.988235); fixed-intersection J=1; no removed cell was top M3/M4.
  Supported tiny-count `JKT_R050_C061` remains a valid 0.
- Required outputs: `eligibility_by_model.csv`, `demographic_support_sensitivity.csv`,
  `demographic_changed_priorities.csv` exist **in candidate paths** (`data/processed/modeling_remediation`,
  `outputs/remediation/tables`), deliberately not in baseline paths.
- Open: DM-01 canonical corrected surfaces/support/version from A2 (support here is auditor mask evidence, not a raster
  repair); MD-01 construct/missingness policy; rerun on integrated candidate. No age values fabricated.

### MD-02 — P1 — Isolate incremental effects — **PARTIAL** (numerics PASS; interpretation decision pending)

- Finding/root: M3→M4 changes weights and constructs simultaneously; rank change read as added information.
- Files: `jhim/remediation.py`, `scripts/{run,verify}_agent3_remediation.py`, `tests/agent3/test_remediation.py`,
  `docs/{research_decisions.md,model_specification.json}`; tables `component_contributions.csv`,
  `rank_change_attribution.csv`, `ablation_comparison.csv`, `normalization_anchors.csv`; figures
  `component_contributions`, `matched_weight_priority_shifts`, `matched_park_increment`.
- Correction: per-grid normalized/weighted terms; exact ΔS = −.1L −.1V −.3P +.25A +.25D; fixed-ID/fixed-anchor
  ablations at 5/10/20%; exact 3-factor Shapley rank allocation with order min/max.
- Tests/results: contribution sums and decomposition < 1e-10 (verified 2.5e-16); Shapley efficiency 2.3e-13.
- Effect (n=2526, top 253, Jaccard vs M4; top5/10/20): total-count swap .969/.977/.996 (retain 250); age share
  .270/.349/.477 (131); child share J10 .458; elderly share J10 .394; no park .427/.425/.524 (151); no demography
  .618/.654/.739 (200); proportional M3+park .924/.917/.954 (242); park only J10 .029; M3 J10 .417 (149).
- **New result-level finding:** in the largest M3→M4 movers the age-swap Shapley share is ≤ 12 ranks, while the park
  term contributes ≈ +360 (gains, distance >1000 m capped) and ≈ −905…−932 (losses, cells 57–89 m from a candidate
  park). M3→M4 reranking is driven by the park-proxy term and reweighting, not by age-count information; age count
  and total count are nearly interchangeable (J10 .977). Age **share** varies only 0.289–0.302 (p05–p95) in banded
  levels, so share-based rankings (J10 .35) rest on <1.3 percentage-point differences of modeled age structure — a
  reason for caution before treating composition as a distinct signal.
- Open: MD-01 signed interpretation; AC-01/02 canonical park proxy. Arithmetic attribution ≠ causation.

### MD-03 — P1 — Scenario families / robustness qualification — **PARTIAL → BLOCKED for access families**

- Finding/root: omnibus OAT median/frequency omitted destination/connector families.
- Files: `jhim/{remediation,sensitivity}.py`, `docs/{scenario_registry.csv,research_decisions.md}`; tables
  `robustness_by_family.csv`, `robustness_family_summary.csv`, `joint_scenario_priority_sets.csv`,
  `joint_scenario_stability.csv`; figure `scenario_family_stability`; dashboard warning.
- Correction: registry with executed/BLOCKED/CONDITIONAL families; eligibility-changing vs fixed-intersection
  comparisons; 16-scenario bounded joint factorial (count construct × cap × normalization × aggregation).
- Tests: `test_real_scenario_membership_recomputes_reported_overlaps` (independent rerank of registry members).
- Effect (fixed intersection, top 10% J min–max): weights .867–.954 (9); normalization .739–.833 (3); park threshold
  .524–.675 (4); population construct .349–.977 (2); land cover .782; aggregation .888; joint factorial .581–.733
  (16); thermal/QA/missing-support 1.0. No blanket robustness claim; frequency is not probability.
- BLOCKED: AC-01 destination/positive-only and AC-02 entrance/barrier per-grid routes (A2); RS-01 seasonal composite
  (A1); TM-02 only if historical claims retained. Auditor aggregate Jaccard values not used as per-grid substitutes.
- Decision: coordinator must sign the scenario envelope.

### EL-01 — P1 — Complete-case selection — **PARTIAL** (local numerics PASS)

- Finding/root: shared universe conditions on route availability (226 route-missing + 1 thermal QA).
- Files: `jhim/remediation.py`; tables `eligibility_selection_profile.csv`, `selection_membership.csv`,
  `missing_access_bounds.csv`, `full_area_vs_common_city.csv`, `m{1,2,3}_{model_specific,common}_eligibility.csv`,
  `full_thermal_top_lost.csv`; figures `eligibility_and_excluded_priority_map`, `model_specific_vs_common`.
- Correction: profiles over all master IDs; explicit model-specific vs common universes; unknown park deficit
  bounds [0,1] (score interval width .25) without filling observed columns.
- Tests/results: 2765 master; route 226; thermal 1; demographic 19 (7 overlap route) → 239 excluded; full-thermal top
  277 loses 18 in common comparison; bounds width .25 — all asserted. Model-specific n: M1/M2 2764, M3 2758.
  City example (M1 top, model-specific → common): Utara 92→77, Timur 92→87 — route-missing concentration shifts
  city shares.
- Open: richer A2 per-destination/connector attributes; final canonical inputs; MD-01 missing-access policy.

### RS-02 — P1 — Thermal support vs delivery — **PARTIAL** (scenarios PASS; threshold decision pending)

- Finding/root: delivered low-support cell treated like missing delivery; .50 threshold provisional.
- Files: `jhim/remediation.py`, `jhim/data.py` (numeric QA flag parsing), `tests/agent3/test_data_contract.py`;
  `rs_eligibility_sensitivity.csv`, `rs_scenario_membership.csv`, `rs_target_support.json`; research decisions.
- Results: `JKT_R037_C062` delivered, LST 42.234 °C, NDVI .2961; support 6724.1312/24223.1114 = .277592
  (nominal coverage .096892, different denominator). .25 or include-flagged: n 2526→2527, target eligible,
  top 5/10/20 J=1. .50 + `rs_qa_ok`: n 2515, top10 J .996047 (one cell left). Values/flags unchanged.
- Open: RS-01 support/provenance from A1; coordinator primary threshold (recommendation: keep .50 + .25 sensitivity).

### ST-01 — P1 — Spatial inference convention — **PARTIAL** (explicit and reproducible; family approval pending)

- Finding/root: esda local default implicit; family/resolution not stated.
- Files: `jhim/{spatial,pipeline,remediation}.py`, `docs/spatial_inference_spec.md`,
  `spatial_weight_manifest.json`, `spatial_weight_neighbors.csv`, `lisa_tail_permutation_{sensitivity,grid}.csv`,
  dashboard spatial page.
- Results (M4, Queen, n=2526, 18336 directed pairs, no islands; per-map family): directed 999 BH 718, two-sided 999
  BH 560; directed 9999 BH 703, two-sided 9999 BH 527; **BY: 0 at 999 (resolution-limited), 274 directed / 180
  two-sided at 9999**; uncorrected p<.05 1141 (directed 999). Labels are convention-sensitive; BY at 999 cannot
  reject anything. Manual Moran I .5921407; SciPy BH/BY reproduce labels. No p=0 claim.
- Open: coordinator approval of tail/family; final source set. Clusters are descriptive only.

### NV-02 — P1 — Geographic comparisons and benchmark — **PARTIAL** (figures/benchmarks PASS locally)

- Files: `jhim/remediation.py`, `outputs/remediation/figures/*`, `outputs/remediation/paper/figure_manifest.csv`,
  `benchmark_comparison.csv`, `geographic_cases.csv`, `docs/external_validation_scope.md`.
- Results: all eight figures inspected visually this session (defects listed in §2 fixed). Benchmarks on same 2526
  IDs: heat-only J top5/10/20 .309/.386/.484 (retain 141 at 10%); equal-weight .881/.867/.924 (235). Cases (grid,
  city, Δrank): gains JKT_R033_C042 Timur +472, JKT_R049_C047 Utara +458, JKT_R044_C005 Barat +457,
  JKT_R038_C020 Barat +453; losses JKT_R034_C030 Selatan −1061, JKT_R047_C011 Barat −1057, JKT_R050_C031 Pusat
  −1055, JKT_R050_C011 Barat −1048. Same-input benchmarks are **not** independent validation; no external
  heat-health/policy outcome is available or claimed.
- Open: AC-01/02 dated park/entrance evidence for case review; NV-01 claim scope; no neighbourhood names invented.

### IN-03 — P1 — Manifests and stale-output detection — **PARTIAL** (local PASS incl. two-run replay; IN-01/02 pending)

- Finding/root: old manifest compared input hashes only and recorded defaults, not actual overrides.
- Files: `jhim/{provenance,pipeline,config}.py`, `scripts/{run_agent3_pipeline,check_agent3_replay}.py`, tests,
  `run_manifest.json` (schema 2), `output_sha256_manifest.csv`, `requirements-agent3.lock`.
- Results: mutation tests (config, code, runtime perms, support file, output content) mark stale; actual top budget
  preserved; **two identical runs certified** (§1). GPKG byte identity reported separately from semantic identity.
- Open: IN-01 clean consolidated candidate (current git identity is `f9b5c02-dirty` + per-file hashes), IN-02 fresh
  environment lock (`requirements-agent3.lock` is a local snapshot).

### UI-01 — P1 — Dashboard scope and missingness — **PARTIAL** (local PASS; integrated-candidate check required)

- Files: `dashboard/{app.py,README.md}`, `dashboard/lib/{ui,context,maps}.py`, `dashboard/views/*`,
  `tests/agent3/test_dashboard_app.py`, `scripts/check_agent3_dashboard.py`,
  `outputs/qa/dashboard_scientific_scope_check.md`, screenshots `outputs/remediation/qa/dashboard/`.
- Results: §1 browser and AppTest coverage (real/no-RS, corrected, demo; custom weights; missingness filter; LISA tail
  × correction). Untested vs non-significant LISA state fixed this session.
- Open: audit acceptance explicitly requires screenshots/interactions on the **final integrated candidate**; final
  wording depends on TM-01/MD-01; minor items listed in the scope-check file.

## 4. Preserved baseline, candidate and source/generated inventory

- Baseline (unchanged, byte-checked by verifier): `data/processed/modeling`, `outputs/tables`, `outputs/figures`,
  `outputs/gis`.
- Frozen inputs: `data/processed/remediation_inputs` + `input_lineage.json` (audited merged/priority/spatial copies,
  auditor raster support and network; derived local RS copied from audited merged table — not RS acquisition).
- Generated candidate: `data/processed/modeling_remediation`, `outputs/remediation/{tables,figures,gis,paper,qa}`.
- Source (implementation identity hashes `jhim/`, `dashboard/`, `scripts/` `*.py`, `docs/model_specification.json`,
  `docs/scenario_registry.csv`, `docs/spatial_inference_spec.md`, `requirements-agent3.lock`): see
  `run_manifest.json` → `implementation.files`. Tests (`tests/agent3`) are not part of that identity.
- Environment: Python 3.12.10 `.venv`; pandas 3.1.1, numpy 2.5.5, geopandas 1.2.0, libpysal 4.15.1, esda 2.10.0,
  scipy 1.18.1 (from manifest).

## 5. Integration interfaces (downstream)

- A2 → DM-01: `JHIM_DEMOGRAPHIC_SUPPORT` (full-ID support CSV, Boolean flags, `support_version`) and
  `JHIM_DEMOGRAPHIC_CORRECTED` (nullable corrected values); contract in `docs/demographic_model_interface.md`.
- A2 → AC-01/02/BG-01: per-grid route/destination/entrance/aggregation versions keyed by `grid_id`; registry rows
  currently BLOCKED become executable families once files exist.
- A1 → RS-01: `JHIM_RS_PATH` canonical `remote_sensing_grid.csv` with support/QA columns; the skipped test activates.
- Integration owner → IN-01/02: one clean commit candidate, fresh lock, then rerun §1 commands and the dashboard check
  on that candidate. Any new canonical input requires a new versioned frozen input path (existing frozen files are
  hash-guarded).

## 6. Human decisions still unsigned (not promoted to official)

TM-01 mixed-reference-period framing; MD-01 count vs composition, weights, normalization, cap, missingness; RS-02
primary thermal threshold; MD-03 scenario envelope; ST-01 tail and testing family; NV-01/QA-01 novelty and claim
scope. Proposals: `docs/research_decisions.md`, `docs/model_specification.json`.

## 7. Readiness

Ready for integration **only as the verified Agent 3 local workstream**: implementation, tests, two-run replay,
independent verification and local dashboard checks pass on frozen audited-derived inputs. Not claimed: canonical
A1/A2 inputs, integrated-candidate tests/UI, fresh environment, scientific sign-off, independent re-audit, or paper
readiness of the project.
