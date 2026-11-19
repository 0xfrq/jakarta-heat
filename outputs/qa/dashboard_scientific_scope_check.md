# Dashboard scientific scope check — UI-01 (Agent 3 local workstream)

Date: 20 November 2026 WIB. Worktree `D:\jakarta-heat-agent3`, branch `agent/person3` (uncommitted).
**Scope boundary:** this checks the Agent 3 corrected *local workstream* (frozen audited-derived inputs in
`data/processed/remediation_inputs`). It is **not** a check of the final integrated candidate, which does not yet
exist (DM-01, AC-01/02, RS-01, IN-01/02 outstanding). UI-01 acceptance requires repeating these checks on that
candidate; this file does not claim it.

## Evidence

| Evidence | Path | Result |
|---|---|---|
| Browser run, 8 routes, corrected data | `outputs/remediation/qa/dashboard/browser_check.json`, `outputs/remediation/qa/browser_check_final.log` | see "Browser result" below |
| Desktop 1440 px / narrow 390 px full-height screenshots | `outputs/remediation/qa/dashboard/page_{0,1,3,5,6,7}_{desktop,narrow}.png` | inspected visually (pages 0, 1, 5, 6 desktop/narrow sampled; 7 narrow) |
| Interaction screenshots | `outputs/remediation/qa/dashboard/interaction_spatial_two_sided_BY_desktop.png`, `interaction_custom_weights_desktop.png` | inspected |
| AppTest (headless Streamlit) | `tests/agent3/test_dashboard_app.py`; results in `outputs/remediation/qa/pytest_final.log` | all 8 routes × real (no-RS) / corrected; 4 routes demo; custom weights; missingness filter; LISA tail × correction controls |

Modes covered: **real/no-RS** (local `data/processed/remote_sensing_grid.csv` absent → model pages show
"belum tersedia" pending warnings, no substitute values), **corrected candidate** (`JHIM_INPUT_DIR` frozen
inputs + `JHIM_DEMOGRAPHIC_SUPPORT`), **DEMO** (always labelled "MODE DEMO — DATA SINTETIS").

## Checklist (audit UI-01 recommended actions)

| Requirement | Where checked | Status in this workstream |
|---|---|---|
| Mixed reference periods, not blanket "2024" (TM-01 wording) | shared banner on all 8 routes (`dashboard/lib/ui.py::banner`), sidebar unit note; browser `mixed_period_visible=true` on 8/8 | PASS locally; final wording depends on signed TM-01 |
| OSM candidate-park **proxy**, not verified 2024 public access (AC-01) | banner, model formula labels "proksi taman kandidat" | PASS locally; AC-01/02 evidence pending |
| Delivery completeness separate from QA/eligibility/support | "Status masukan: COMPLETE" = structural delivery; separate caption for thermal-QA exclusion `JKT_R037_C062`; separate support warning (19 age-unsupported grids, n=2526 shared set) | PASS locally |
| Unknown ≠ zero / no access | null analytical values for unsupported cells; missing-legend states on maps ("kosong / tidak dipakai", "rute tidak dihitung (226)"); explorer summary "Kosong: 6 grid" for unsupported total population | PASS locally |
| LISA: tested-not-significant vs untested | **Fixed this session**: legend previously merged both into "tidak signifikan / tidak diuji (2,765)"; now "tidak signifikan (diuji)" vs "tidak diuji (tidak layak / island)", caption with n significant / tested / untested; info note when BY/BH yields zero because of permutation resolution | PASS locally (AppTest + browser) |
| Tail and correction controls | spatial page: alternative directed/two-sided; BH / BY / uncorrected; permutation slider | exercised by AppTest (all 6 combinations, 99 perms) and browser (two-sided, BY, uncorrected at 999) |
| Scenario frequency ≠ probability; OAT ≠ all-family robustness | robustness page warning box + banner; OAT summary (24 scenarios, median J top10 0.90, min 0.35, 78% stable) is explicitly labelled one-at-a-time only | PASS locally; family envelope unsigned (MD-03) |
| Baseline vs custom weights | priority page toggle "Bobot eksploratif (bukan baseline)" → "EKSPLORATIF" warning | PASS (AppTest + browser) |
| Missingness filters | explorer multiselect of flags incl. `qa_age_source_no_support` (19 rows) | PASS (AppTest) |
| Provisional/unsigned decisions visible | banner "Bobot dan kebijakan ilmiah belum disahkan tim"; formula table "PROVISIONAL" | PASS locally |
| Demo visibly synthetic | DEMO error banner on every demo page | PASS (AppTest + browser) |
| Downloads carry reference/policy metadata | `ui.download` | implemented by previous Agent 3 session; not re-inspected file-by-file here |
| Narrow readability | narrow screenshots now taken with collapsed sidebar and full content height (previous screenshots were viewport-only and one showed the sidebar overlay mid-transition) | readable; wide tables scroll horizontally inside their frame |

## Browser result (final source)

From `outputs/remediation/qa/dashboard/browser_check.json` (final source, Edge headless, port 8543):
8/8 routes rendered with 0 Streamlit exceptions and 0 page errors; `mixed_period_visible` and
`corrected_n_visible` (2,526) true on 8/8; narrow sidebar collapsed on all screenshotted routes. Interactions
(all OK, expected text visible, no exceptions): LISA alternative two-sided; BY correction; uncorrected p<0.05;
exploratory custom weights ("EKSPLORATIF"); DEMO mode ("MODE DEMO"); back to real data (support warning).
AppTest: `tests/agent3/test_dashboard_app.py` within the 116-passed final suite.

## Remaining observations (not fixed; recorded honestly)

- Methods page contains two `h1` headings (page title plus a markdown `#` heading). Cosmetic/accessibility only.
- Model-pages metric label "Grid valid data Person 2" uses internal team jargon.
- "Status masukan: COMPLETE" refers to structural delivery of the frozen *audited-derived* inputs; the RS values
  are copied from the audited merged table because the canonical Agent 1 export is absent (RS-01). The banner
  does not say "audited-derived"; the methods doc and manifest do.
- Pydeck basemaps load OSM/CARTO tiles over the network; offline viewing shows grids without basemap.
- Not every widget combination is exercised; coverage is the sampled set listed above.
