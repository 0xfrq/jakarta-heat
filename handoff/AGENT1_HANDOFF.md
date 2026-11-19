# Agent 1 Handoff — Remote Sensing Workstream (Person 1)

Project: Jakarta Heat Inequality Mapper · Study area: five mainland cities of DKI Jakarta
(Kepulauan Seribu excluded) · Year: 2024 · Unit: 500 m master grid (2,765 cells)
Branch: `agent/person1` (worktree `D:\jakarta-heat-agent1`) · Updated: 2026-11-20

**Current status: numerical R2 delivery COMPLETE; RS-01 provenance BLOCKED; R3 PARTIAL.**
R2 (LST + NDVI) arrays and aggregation are verified locally. 2024 is the intended
recipe period; historical scene dates/task identity/AOI version have not been recovered.
R3 is partial: Dynamic World *probability* features are complete; Dynamic
World *class fractions* (`tree_fraction`, `grass_fraction`, `built_fraction`) are **BLOCKED** by
Earth Engine access (script ready, columns present but empty, never zero-filled).

**Remediation supersedes the historical details below:** see
`handoff/REMEDIATION_AGENT1.md`, `docs/remote_sensing_deliverable_status.md`, and
`docs/remote_sensing_reproduction.md`. The authoritative issue IDs are RS-01 and
DW-01; legacy RS-03/RS-04 notes in the audit's RS evidence are consolidated in DW-01.
The original canonical 30-column outputs remain the audited baseline. Proposed
42-column revised outputs are in `data/processed/remote_sensing_remediated/`.
They fix area precision and the future categorical denominator, without changing
any LST/NDVI/probability/flag value. Categorical `*_fraction` now means whole clipped
polygon area; `*_fraction_valid` separately means valid-labelled area. Actual
categorical export is still absent; coordinator deferral/retention approval is pending.
Forty tests, 49 validator checks and 140 independent pixel intersections pass;
two isolated builds agree in numeric values and geometry. Actual local M1–M4
scores/ranks on the fixed legacy 2,538 IDs are unchanged by the RS input revision.
RS-02 threshold/reranking ownership remains Agent 3. No consolidated release or
scientific gate is certified by this handoff. Sections 1–15 describe the 2026-11-19
baseline unless explicitly updated above.

---

## 1. Initial audit (state before Agent 1 changes)

| Component | Location | Classification | Evidence |
|---|---|---|---|
| GEE script, Landsat 9 LST/NDVI + DW probabilities | `scripts/02_remote_sensing_gee.js` | IMPLEMENTED, executed, unverified → now **VERIFIED** | Correct collection, L2SP filter, 2024 start-inclusive/end-exclusive, QA_PIXEL bits 0–5 + QA_RADSAT, official C2 scaling. Header comments were stale (said "temporary rectangle", "4 bands") |
| Landsat composite raster | `data/processed/remote_sensing/jakarta_2024_lst_ndvi_qa.tif` (9.2 MB, committed in `19fa2a3`) | REAL OUTPUT, unverified → now **VERIFIED** | 1058×1042 px, 30 m, EPSG:32748, 5 bands |
| DW probability raster | `data/processed/remote_sensing/jakarta_2024_trees_built_probability.tif` (57 MB, committed) | REAL OUTPUT, unverified → now **VERIFIED** | 3174×3124 px, 10 m, 2 bands (`trees_prob`, `built_prob` = median per-image probability) |
| "Thermal feature" | `qgis/thermal_features.qgz` | **PARTIAL / BROKEN** | A QGIS project of 7 manual Zonal Statistics steps (`lst_mean`, `ndvi_mean`, `unc_mean`, `obs_mean`, `valid_mean`, `trees_mean`, and step 7 *also* named `trees_mean` — evidently the built layer mislabelled). Outputs referenced at `../../processing/thermal_step*.gpkg` do **not exist** anywhere on disk or in the repo; QGIS zonal stats use pixel-centroid inclusion (not area-weighted). Not reproducible from code. |
| QA report | `docs/landsat_quality_report.md`, `docs/*_metadata.json` | IMPLEMENTED, preliminary | Statistics at 100 m sampling; 7 pending checks |
| `data/processed/remote_sensing_grid.csv` | — | **MISSING** | Only `data/processed/dummy/remote_sensing_grid.csv` (`is_dummy=1`) existed |
| DW class fractions / grass | — | **MISSING** | Existing export has no `label` and no `grass` |
| Earth Engine access from this machine | — | **BLOCKED** | No `earthengine` credentials; Chrome extension not connected. GEE was used via the browser Code Editor (asset project `nodemailer-mailer`) |

Person 2 claims verified on `data/processed/spatial_features.csv`: 2,765 rows / 2,765 unique IDs;
population, pop_child, pop_elderly 0 missing; `park_distance_m` 226 missing and 0 zero values;
66 grids with `grid_snap_m > 250`. All confirmed.

Dashboard/`jhim` contract (Agent 3, read-only): `jhim/config.py` requires `grid_id, lst_c, ndvi`
in `data/processed/remote_sensing_grid.csv`; extra columns are ignored; plausible ranges
LST 15–60 °C, NDVI −1..1. Not modified.

## 2. Existing files reused
- Both GeoTIFFs above (no re-download or recomputation; they are the real GEE exports of the
  committed script).
- `data/processed/grid_500m_jakarta.gpkg`, `data/processed/grid_master.csv` (Person 2).
- `scripts/02_remote_sensing_gee.js` (logic unchanged; only comments added).

## 3. Files created / modified

| File | Status | Purpose |
|---|---|---|
| `scripts/02b_aggregate_remote_sensing.py` | new | Raster → 500 m grid aggregation, writes CSV/GPKG/meta |
| `scripts/02c_dynamic_world_fractions_gee.js` | new | GEE: annual modal DW label (for class fractions) — **not yet run** |
| `scripts/02d_validate_remote_sensing.py` | new | 46 contract/raster/independent-recomputation checks + QA outputs |
| `tests/test_remote_sensing_grid.py` | new | 22 pytest contract tests |
| `requirements-remote-sensing.txt` | new | Pinned environment |
| `data/processed/remote_sensing_grid.csv` | new | **Main deliverable** (366 KB) |
| `data/processed/remote_sensing_grid.gpkg` | new | Same + geometry, layer `remote_sensing_grid` (1.3 MB) |
| `data/processed/remote_sensing_grid.meta.json` | new | Provenance, input SHA-256, reducers, summary statistics |
| `data/processed/remote_sensing_qa_problem_grids.csv` | new | 110 flagged grids with coordinates |
| `outputs/qa/remote_sensing_qa.json` | new | Validation results |
| `outputs/maps/remote_sensing_grid_preview.png` | new | 6-panel QA map |
| `scripts/02_remote_sensing_gee.js` | modified | Header comments corrected + audit note (no logic change) |
| `docs/landsat_quality_report.md` | modified | Pending-validation checklist resolved with evidence |
| `docs/landsat_metadata.json`, `docs/dynamic_world_metadata.json` | modified | Validation status, nodata semantics, blocked status |
| `handoff/AGENT1_HANDOFF.md` | new | This document |

Not touched: `dashboard/`, `jhim/`, Person 2 scripts and data.

## 4. Input data and periods
- **Landsat 9 Collection 2 Tier 1 Level-2** (`LANDSAT/LC09/C02/T1_L2`), `PROCESSING_LEVEL == 'L2SP'`,
  2024-01-01 (inclusive) to 2025-01-01 (exclusive). Sensor: OLI-2 (SR) and TIRS-2 (ST, band 10).
  Scene count not recorded (needs GEE); per-pixel clear observations 3–28.
- **Dynamic World V1** (`GOOGLE/DYNAMICWORLD/V1`, Sentinel-2 based, 10 m), same period;
  94 images intersecting the AOI (from `docs/dynamic_world_metadata.json`).
- AOI: GEE asset `projects/nodemailer-mailer/assets/jakarta_5kota` (five cities); grid from
  `data/processed/grid_500m_jakarta.gpkg` (EPSG:32748, polygons clipped to the boundary).

## 5. Algorithms and formulas (verified against the USGS C2 L2 product guide)
Per scene (GEE):
- Clear mask: `QA_PIXEL & 0b111111 == 0` (fill, dilated cloud, cirrus, cloud, cloud shadow, snow)
  and `QA_RADSAT == 0`.
- LST: `T_K = ST_B10 × 0.00341802 + 149.0`; `LST_°C = T_K − 273.15` (single scaling — confirmed by
  pixel range 29.36–57.08 °C; a double-scaled or unscaled band would be far outside this).
- Reflectance: `ρ = DN × 2.75e-05 − 0.2` for `SR_B4` (red) and `SR_B5` (NIR);
  `NDVI = (ρ_NIR − ρ_red)/(ρ_NIR + ρ_red)`, masked where |denominator| ≤ 1e-6.
- `lst_unc_k = ST_QA × 0.01` (per-scene retrieval uncertainty, K).
- ST fill: GEE masks `ST_B10` fill; evidence: 78 in-AOI pixels have valid NDVI but no LST, and
  no scaled-fill value (≈ −124 °C) appears in the raster.

## 6. Reducers
- **Temporal (within 2024, per pixel):** median of clear observations, each band independently
  (`ImageCollection.median()`). LST and NDVI therefore share the same clear-sky mask but their
  medians can come from different dates. `lst_obs` = count of clear LST observations.
  DW: median of per-image `trees` / `built` probabilities. *The primary LST variable is the
  annual median of valid clear-sky observations (provisional default, as in the original
  script). It is a summary of ~10:30 local-time clear-sky overpasses, not a continuous or
  daytime-average measurement.*
- **Spatial (within each 500 m cell):** exact pixel-coverage-weighted mean (exactextract 0.3.0):
  a pixel 30 % inside a cell has weight 0.3; nodata/NaN ignored. Valid fractions = Σ(coverage of
  valid pixels) × pixel area / cell polygon area.

## 7. Output paths
- `data/processed/remote_sensing_grid.csv` — canonical deliverable
- `data/processed/remote_sensing_grid.gpkg` — QA/inspection layer
- `data/processed/remote_sensing_grid.meta.json` — provenance + summary
- `data/processed/remote_sensing_qa_problem_grids.csv`, `outputs/qa/remote_sensing_qa.json`,
  `outputs/maps/remote_sensing_grid_preview.png`

## 8. Schema (`remote_sensing_grid.csv`, 2,765 rows, 30 columns, master-grid order)

| Column | Unit | Definition | Missing |
|---|---|---|---|
| `grid_id` | — | Master grid ID, `JKT_Rrrr_Cccc` | 0 |
| `lst_mean_c` | °C | Coverage-weighted cell mean of the 2024 per-pixel median LST | 0 |
| `ndvi_mean` | — | Coverage-weighted cell mean of the 2024 per-pixel median NDVI | 0 |
| `tree_fraction` | 0–1 | Share of cell area whose annual modal DW label = trees | **2,765 (BLOCKED)** |
| `grass_fraction` | 0–1 | … = grass | **2,765 (BLOCKED)** |
| `built_fraction` | 0–1 | … = built | **2,765 (BLOCKED)** |
| `lst_valid_fraction` | 0–1 | Share of cell area covered by pixels with ≥1 clear LST obs | 0 |
| `lst_observation_count` | count | Coverage-weighted mean, over valid pixels, of clear LST observations per pixel in 2024 | 0 |
| `lst_std_c` | °C | Coverage-weighted within-cell SD of pixel median LST | 0 |
| `lst_min_c`, `lst_max_c` | °C | Min/max pixel median LST touching the cell | 0 |
| `lst_unc_mean_k` | K | Cell mean of the per-pixel *median* ST_QA (not the uncertainty of the median) | 0 |
| `lst_observation_min` | count | Minimum per-pixel clear-observation count in the cell | 0 |
| `ndvi_std` | — | Within-cell SD of NDVI | 0 |
| `ndvi_valid_fraction` | 0–1 | Share of cell area with valid NDVI | 0 |
| `landsat_footprint_fraction` | 0–1 | Share of cell area inside the exported raster AOI (any value incl. -9999) | 0 |
| `tree_prob_mean` | 0–1 | Cell mean of the median DW `trees` probability (**probability, not area fraction**) | 1 |
| `built_prob_mean` | 0–1 | Cell mean of the median DW `built` probability (**probability, not area fraction**) | 1 |
| `dw_valid_fraction` | 0–1 | Share of cell area with DW probability data | 0 |
| `water_fraction`, `flooded_vegetation_fraction`, `crops_fraction`, `shrub_fraction`, `bare_fraction` | 0–1 | Other DW modal-label class fractions | 2,765 (BLOCKED) |
| `dw_label_valid_fraction` | 0–1 | Share of cell area with a DW modal label | 2,765 (BLOCKED) |
| `qa_area_km2` | km² | Clipped cell polygon area (matches `grid_master.area_km2` within 5e-7) | 0 |
| `rs_qa_flags` | text | `;`-separated: `no_lst`, `partial_lst` (<0.5 valid), `low_obs` (<5), `high_unc` (>5 K), `edge_cell` (<0.05 km²), `footprint_gap` (<0.98) | empty = no flag |
| `rs_qa_ok` | bool | False if `no_lst`, `partial_lst`, `low_obs` or `high_unc` | 0 |
| `lst_c` | °C | **Compatibility alias** = `lst_mean_c` (jhim/dashboard contract) | 0 |
| `ndvi` | — | **Compatibility alias** = `ndvi_mean` | 0 |

## 9. Row counts and coverage statistics (actual)
- 2,765 rows; 2,765 unique IDs; ID set and order identical to `grid_master.csv`.
- `lst_mean_c`: min 31.12, P5 36.83, median 41.72, mean 41.39, P95 44.53, max 47.92 °C.
- `ndvi_mean`: min −0.056, P5 0.163, median 0.304, mean 0.319, P95 0.526, max 0.795.
- `lst_valid_fraction`: 2,760 cells ≥ 0.99; min 0.278. `landsat_footprint_fraction` ≥ 0.989.
- `lst_observation_count`: min 5.96, median 10.0, P95 20.0, max 27.4.
- `tree_prob_mean` median 0.042 (max 0.646); `built_prob_mean` median 0.673 (max 0.738).
- City medians (LST °C / NDVI): Barat 41.85/0.265 · Pusat 41.47/0.256 · Selatan 41.49/0.359 ·
  Timur 42.17/0.325 · Utara 41.32/0.253.
- Correlations (cell level): LST–NDVI −0.62; LST–built_prob +0.75; NDVI–tree_prob +0.76.

## 10. Missing values and QA findings
- **No LST/NDVI is missing at grid level.** 78 in-AOI pixels lack any clear LST observation;
  they sit at the eastern boundary of Jakarta Timur and reduce `lst_valid_fraction` in
  JKT_R037_C061 (0.878), JKT_R037_C062 (0.278, flagged `partial_lst`), JKT_R038_C061 (0.978),
  JKT_R038_C062 (0.889). Their means use the remaining valid pixels.
- JKT_R042_C004 is a sliver (< 1 m²) with no DW pixel → `tree_prob_mean`/`built_prob_mean` empty.
- 12 cells `high_unc` (mean ST_QA 5.0–5.75 K), mostly northern coast/industrial.
- 101 `edge_cell` (< 0.05 km²): means rest on very few pixels; `lst_std_c` can be 0.
- Flag totals: partial_lst 1, high_unc 12, edge_cell 101, low_obs 0, no_lst 0, footprint_gap 0;
  `rs_qa_ok` True for 2,752 cells.
- Extreme pixels: 57.08 °C (JKT_R054_C056/C057, Cilincing–Marunda port/industrial),
  56.56 °C (JKT_R044_C054, Pulogadung industrial estate). Plausible industrial surfaces; kept.
- Temporal support is uneven: southern strip ~20–27 clear obs vs ~8–12 elsewhere (scene overlap).
- Missing values are written as empty cells; nothing is zero-filled or imputed.

## 11. Tests executed (2026-11-19)
- `python scripts/02d_validate_remote_sensing.py` → **46 checks, 0 critical failures** (ID contract,
  one-to-one join with `spatial_features.csv`, unit/range checks, alias identity, fraction ranges,
  raster nodata semantics, no leaked ST fill, independent analytic recomputation of LST/NDVI/DW
  means on 25 full cells: max |Δ| 0.00046 °C, 0.00005 NDVI, 0 DW).
- `python -m pytest tests/test_remote_sensing_grid.py -q` → **22 passed**, including loading the file
  through Agent 3's `jhim.data.read_input_csv`.
- In-memory dry run of `jhim.data.merge_inputs` + `clean_values` with real data (no files written):
  LST/NDVI missing 0, 2,539 valid grids; the 226 exclusions come only from `park_distance_m`.

## 12. Reproduction
```powershell
# 1) Earth Engine (Code Editor, account with access to projects/nodemailer-mailer):
#    run scripts/02_remote_sensing_gee.js -> Tasks -> run both exports (only needed to rebuild rasters)
#    run scripts/02c_dynamic_world_fractions_gee.js -> Tasks -> JKT_2024_DW_label_mode
#    download the GeoTIFFs from Drive folder Jakarta_Heat_Project into data/processed/remote_sensing/
# 2) Local environment (Python 3.12)
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements-remote-sensing.txt
# 3) Aggregate, validate, test
.venv\Scripts\python scripts/02b_aggregate_remote_sensing.py
.venv\Scripts\python scripts/02d_validate_remote_sensing.py
.venv\Scripts\python -m pytest tests/test_remote_sensing_grid.py -q
```
When `jakarta_2024_dw_label_mode.tif` is present, step 3 fills the class-fraction columns
automatically and the tests switch to checking that fractions sum to ~1.

## 13. Blockers and scientific caveats
- **BLOCKED:** DW class fractions (tree/grass/built/…): needs one run of
  `scripts/02c_dynamic_world_fractions_gee.js` by someone with GEE access, then re-run step 3.
  The DW-probability columns must not be relabelled as fractions in the meantime.
- **Not done (needs GEE):** Landsat scene count; seasonal/dry-season sensitivity composite.
- LST is land *surface* temperature from clear-sky ~10:30 overpasses; not air temperature, heat
  index or physiological heat stress; clear-sky sampling biases toward drier conditions.
- The annual median is not an annual mean nor a continuous measurement.
- Landsat TIRS native resolution is 100 m (resampled to 30 m by USGS); within-cell LST SD is
  partly smoothing.
- `lst_unc_mean_k` summarises per-scene retrieval uncertainty, not the uncertainty of the median.
- DW is Sentinel-2-based (10 m) with different dates from Landsat 9; tree cover/probability is
  not public park access.
- No ground validation of LST was performed.

## 14. What Agent 3 can consume now
- `data/processed/remote_sensing_grid.csv`, join key `grid_id`, one-to-one with
  `spatial_features.csv`. `lst_c`/`ndvi` already satisfy `jhim.config.RS_COLS`; canonical names are
  `lst_mean_c`/`ndvi_mean` (identical values). Optional QA: `rs_qa_ok`, `rs_qa_flags`,
  `lst_valid_fraction`, `lst_observation_count`. Do not treat empty `*_fraction` as 0.
- No M1–M4 scores, weights or rankings were produced by Agent 1.

## 15. Person 2 checklist for final integration (R7)
- [ ] Confirm the GEE AOI asset `jakarta_5kota` equals `data/processed/jakarta_5kota.gpkg`
      (footprint ≥ 0.989 for every cell suggests yes; slight edge differences remain).
- [ ] Inspect the 4 eastern-boundary cells (JKT_R037/R038_C061–C062) with LST gaps.
- [ ] Decide whether `edge_cell` (101) and `high_unc` (12) cells are kept, down-weighted or excluded.
- [ ] Re-run `scripts/02b…` and `02d…` if the master grid changes (IDs are validated, not assumed).
- [ ] After DW fractions are produced, verify `tree_fraction`/`built_fraction` against
      `tree_prob_mean`/`built_prob_mean` and the parks layer (expect correlation, not equality).
- [ ] Keep the 57 MB DW probability raster and any new 10 m label raster out of further commits
      unless the team agrees (use Drive/LFS).
