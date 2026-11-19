# AGENT2 HANDOFF — GIS, accessibility, spatial QA and integration

> **KOREKSI STATUS (20 November 2026, remediasi pasca-audit).** Status "DONE WITH
> DOCUMENTED LIMITATIONS" di bawah hanya berlaku untuk handover engineering
> sebelum audit independen. Audit membuka tujuh isu P1 milik Agent 2 (AC-01,
> AC-02, DM-01, TM-02, BG-01, IN-01, IN-02); status terkini, bukti, hasil tes dan
> blocker ada di [`REMEDIATION_AGENT2.md`](REMEDIATION_AGENT2.md). Beberapa
> pernyataan lama sudah tidak berlaku: (1) 19 sel usia dan 6 sel total bernilai 0
> adalah jumlah mask kosong, bukan nol sumber — koreksinya di
> `data/processed/demographic_*` dan `*_corrected*`; (2) sumber besar tidak lagi
> dibaca dari `D:/jakarta-heat` — jalur offline memakai input beku lokal
> (`docs/agent2_frozen_inputs.json`, `docs/REPRODUCE.md`); (3) kode Agent 3 beku di
> `outputs/qa/agent2/baseline/agent3` hanya data pembanding, bukan paket yang
> diimpor. Dokumen ini dipertahankan sebagai catatan historis; jangan menjalankan
> ulang `scripts/agent2_write_handoff.py` tanpa meninjau koreksi ini, karena
> renderer tersebut menimpa berkas ini.

Generated UTC: 2026-11-19T17:15:50.635942+00:00. Workspace `D:/jakarta-heat-agent2`.
**Status: DONE WITH DOCUMENTED LIMITATIONS for this engineering/QA handover.**
This is not approval of final scientific rankings, a synchronous 2024 OSM inventory, public entrances,
or the manuscript. Open scientific decisions are in `AGENT2_DECISION_REGISTER.md`.

## 1. Initial audit and safe baseline

| Component | Existing output | Actual validation status at start | Gaps | Action/result |
| --- | --- | --- | --- | --- |
| Boundary/grid | GPKG + master CSV | Exists; earlier integrity assertions only | Independent geometry/clip/city evidence absent | Full lattice/union/owner recomputation; PASS |
| Population/age | 3 CSV + local TIFF | No missing CSV values | Manual QGIS aggregation; provenance not catalogued | TIFF metadata, alignment, hybrid recomputation, mask QA |
| Parks | parks_jakarta.gpkg | Mapped candidates, public entry unverified | Unknown access; original polygons not yet inspected | Recover cache, reproduce polygons, tag/exclusion audit |
| Walking | 5 city outputs + full graph in main repo | 226 unknown routes, 66 far snaps | Cause, crop, barriers and temporal scope unverified | Reproduce routes, components, full graph and gate scenarios |
| Remote sensing | Agent1 committed CSV/GPKG/rasters | 2765 delivered values | Independent alignment/aggregation pending | Exact geometry match + all-grid raster recomputation |
| Models/maps | Agent3 uncommitted working outputs | Provisional 2538 common grids | Need independent GIS/input reconciliation | Freeze code/results; recompute M1-M4 and city summaries |
| Integrated sources | No final_model_features.csv initially | Missing companion integration | Full source population + QA/eligibility separation | Created 2765-row compatible companion table |


| workspace | branch | sha | state |
| --- | --- | --- | --- |
| jakarta-heat | main | f9b5c02ae2782ca00edcc077a29999b7ada3b91b | clean at capture |
| jakarta-heat-agent1 | agent/person1 | cdda42484c6bfc5bceb49093cb4a28be6c59d659 | clean at capture |
| jakarta-heat-agent2 | agent/person2 | f9b5c02ae2782ca00edcc077a29999b7ada3b91b | uncommitted snapshot |
| jakarta-heat-agent3 | agent/person3 | f9b5c02ae2782ca00edcc077a29999b7ada3b91b | uncommitted snapshot |

Initial terminal inspection found Agent2 and main clean at `f9b5c02`; the baseline capture itself
appears as Agent2's first untracked bootstrap script in capture.json. Agent1 was committed at
`cdda42484c6bfc5bceb49093cb4a28be6c59d659`. Agent3 remained uncommitted: all findings here apply
to the frozen, hash-recorded snapshot, not to an assumed stable Agent3 release.
`baseline/capture.json` preserves full status/untracked paths for all four workspaces.
No commit, merge, push, process interruption, or write into other worktrees was performed.

## 2. Original outputs preserved

Original Person2 source CSVs, accessibility CSVs, grid geometry and park GPKG remain unchanged.
Small CSVs and upstream artifacts/code are frozen in `outputs/qa/agent2/baseline/` with SHA-256.
Large GraphML/road/WorldPop files are read directly from `D:/jakarta-heat` without replacing them.
They do not exist automatically in worktrees. No new OSM download or graph construction was needed.
Agent1 real rasters already present locally were reused. Do not run `00_make_dummy_inputs.py` on real inputs.

## 3. Code implemented and defects repaired

- `person2_contracts.py` + repaired `07_integrate_spatial.py`: exact ID sets, nonempty unique keys,
  canonical alias collision rejection, numeric/finite/nonnegative checks, mandatory demographics and snaps,
  legacy route/threshold consistency, 5%+1 person age tolerance matching Agent3, and atomic output.
  The previous join could silently turn an absent population row into a missing feature or ignore an extra ID.
  `--output` permits comparison without overwriting baseline. Rebuilt values match all original source rows.
- `agent2_gis.py`: geography, demographic raster recomputation, parks, city/full network diagnostics,
  all-grid satellite verification, source integration, frozen-engine compatibility, sensitivity and map atlas.
- `agent2_capture_baseline.py`: one-time small-artifact snapshot; refuses to overwrite existing capture.
- `agent2_enrich_evidence.py`: original Overpass park recovery, raw network restrictions and declared extent,
  TIFF alignment, original OSM revision timestamp evidence, bounded primary-document retrieval.
- `agent2_node_restrictions.py`: explicitly labelled conservative node-restriction scenario; fixed original
  snaps, gate-crossing edges removed, no connector resnapping across an excluded gate.
- `agent2_qgis_project.py`: standalone QGIS project with valid source, QA, raster and provisional model layers.
- `tests/test_agent2_gis.py`, pinned `requirements-agent2.txt`, this document renderer.

## 4. Dataset provenance and temporal scope

Boundary: geoBoundaries IDN ADM2, selected five `Kota Jakarta` geometries by existing grid script.
Local source `data/raw/idn_adm2.geojson`; original API metadata JSON is unavailable, so exact boundary
release/source date remains unverified. This is not an assertion of current official cadastral accuracy.

Total population TIFF identifies `idn_pop_2024_CN_100m_R2025A_v1`, WorldPop Global2 R2025A v1,
constrained model estimates, EPSG:4326, 3 arc seconds (~100m), CC BY 4.0. Child/elderly TIFF tags identify
2024, R2025A, both sexes, units `people per cell`, age `0-14` / `65+`, DOI `10.5258/SOTON/WP00841`.
The age download script requests `[65,90]`; TIFF metadata labels its open-ended band `both_65_plus`.
The upstream release defines class 90 as 90 and older. Product identity is supported by embedded tags,
local download code and primary product documentation, not a byte comparison against all original national
age-band downloads. Source population DOI is `10.5258/SOTON/WP00839`.
See `population_rasters.json`, `age_alignment_summary.json`, source hashes and data dictionary.

**OSM is contemporary 2026 ancillary data.** Park cache exact OSM base timestamp is
`2026-11-19T11:02:20Z`. The original network extract contains revisions up to
`2026-11-18T20:09:46Z`; this is a lower bound on extraction date, not an exact snapshot date.
Raw network acquisition URL is not documented. Graph created `2026-11-19 19:54:27`
with OSMnx 2.2.0, filter version2. Do not call these 2024 parks/network without historical reconstruction.

Primary references inspected: [WorldPop API documentation](https://api.worldpop.org/v3/documentation),
[WorldPop R2025A release statement](https://data.worldpop.org/repo/prj/Global_2015_2030/R2025A/doc/Global2_Release_Statement_R2025A_v1.pdf),
[QGIS 3.44 zonal source](https://github.com/qgis/QGIS/blob/release-3_44/src/analysis/vector/qgszonalstatistics.cpp),
[OSMnx API](https://osmnx.readthedocs.io/en/stable/user-reference.html).
Raw HTTP fetches of WorldPop documentation returned a JavaScript shell (only title); these fetches alone
are not source validation. The primary page text was inspected through web search; TIFF provenance is
local and separately inspectable. `official_sources.json` records this limitation.

## 5. Exact GIS methodology

Master lattice is 500 x 500m in EPSG:32748. IDs encode row/column from floored UTM origin.
Each square is clipped to the five-city union; city ownership is maximum polygon overlap.
Grid representative point is guaranteed inside the clipped analysis polygon. Agent3 uses polygon
centroids for x/y descriptive coordinates and actual polygon geometry for Queen adjacency.
City totals here assign each complete clipped grid to its majority-area owner; they are grid-based
summaries, not exact raster zonal totals within each administrative city boundary.

Population aggregation reproduces QGIS Zonal Statistics: sum valid pixels with centers inside polygon;
if valid center count <=1, replace this with fractional pixel-polygon intersection sum. No resampling or
density multiplication is applied. Geographic rasters are used in their native CRS after polygon reprojection.
This is a hybrid raster boundary rule, not exact fractional population allocation for every cell.
An exact-extraction alternative is provided as a sensitivity, not adopted as canonical.

Routing baseline: bidirectional simplified directed multigraph; custom highway/access/foot filter on ways,
all components retained; per-city polygon buffer 1500m; grid point city by point-within test; eligible candidate
parks intersect buffer; nearest projected graph node for origin and park representative point. Cost is
origin straight connector + shortest network edge length + park straight connector. Reverse virtual-source
Dijkstra is mathematically verified on directed/parallel/disconnected toy graphs and against every baseline
route. The new diagnostic implementation avoids materializing all path lists and never changes source graph.

This is approximate proximity to OSM-mapped polygons using a road graph. Neither connector is a verified
walkable path or public entrance. No assumption is made that straight connectors cross barriers legally.

## 6. Grid, coverage and city QA

2765 unique geometries/IDs; five mainland cities; no Kepulauan Seribu; all polygons valid/nonempty;
CRS EPSG:32748. Union area 643.237054631 km². Clip symmetric difference
0.00000344 m²; absolute internal overlap numerical residual <1m².
Every geometry matches its exact 500m lattice square intersected with boundary (error <0.01m²).
383 partial cells; 65 coverage <10%; 101 area <0.05km²;
minimum clipped area 0.422885m². None were automatically deleted.
Distinguish square area 250000m², clipped area, clipped/square ratio, and raster valid-pixel fraction.

14 grid representative points fall in another city than the majority-area owner.
This explains a routing-partition choice, not incorrect canonical city labels. All city summary checks use
the majority-area owner, and baseline routing is reproduced according to its actual point partition.

## 7. Demographic QA and age alternatives

No CSV missing/negative values; total estimated population 10,983,537.125; children
2,567,476.538; elderly 675,277.954; combined
3,242,754.492. Six population-zero cells and 20 zeros in each age group.
No combined age count exceeds total+1 person. Raster origins/resolution align exactly to integer pixels.
All 2765 original hybrid sums reproduce within 0.01 person (maximum total-pop difference
0.001633, child
0.000298, elderly
0.000090). Floating summation precision
explains these small residuals. Original values are preserved.

14 populated grids have both ages zero (together ~65 modeled persons). Of these, **13** have no valid age
pixel support; one has valid age pixels summing to zero and total population ~0.00012. Overall 19 cells
have zero age pixel support, including six population-zero cells. QGIS sum over no valid pixels returns 0;
this is not evidence of no children/elderly. Source zeros stay visible, with `qa_age_source_no_support` and
an exclusion sensitivity. `zero_age_populated_grid_diagnostics.csv` distinguishes the causes per ID.

Population–combined-age Spearman 0.999551376; Pearson
0.999589532. Vulnerable-share median
0.296680; P5–P95 0.289394–0.301561.
Source-integrated `vulnerable_share` is NaN for zero total population (undefined ratio). Agent3's scenario
variable `vuln_share` uses 0 there; this deliberate existing convention is documented and not changed.
Counts represent exposure of age groups; share represents age composition. They are not interchangeable.

## 8. Park inventory and access QA

1015 baseline polygons; no invalid geometries, duplicate IDs or exact duplicate shapes;
577 unnamed, 9.011980km² clipped area. 1005 unknown access;
9 `yes`, 1 `permissive` (positive tags, still not independently verified). Unknown tags are never proof of
unrestricted entry. `leisure=park` excludes gardens and other green-space classes by design; completeness
relative to a municipal public-park inventory is unverified.

Recovered original cache has 1017 polygon candidates; two excluded (`private`,
`permit`). IDs and clipped geometries reproduce current inventory within
0.00000015m². 13 original polygons extend
outside the study, 3 cross internal city boundaries. Original polygons
are now inspectable in QA GPKG; clipping changes their representative points. No new park was silently added.
Sample IDs/access evidence and destination counts are in `park_manual_review_samples.csv` and
`park_samples_qa.png`. Named examples
include RPTRA Rorotan and Taman Sungai Kendal; high-use unnamed polygons are explicitly retained for review.
There was no field visit, verified gate/operating-hours check, or claim that a sampled park is confirmed public.

## 9. Walking graph provenance, filter, connectivity and extent

Full graph 190,367 nodes / 489,672 directed edges, 2033 weak components,
largest 181,148. All retained directed edges have finite nonnegative meter lengths;
every edge has a reverse connection. All five city graph edges/keys/lengths match the common full source;
metadata also identifies offline version2 and 1500m buffer. Old Pusat online backups were not mixed in.
The filter excludes motorways/trunks/construction, area roads, foot=no/private, access=no/private without
explicit foot permission, private service without override, and cycleways absent explicit foot permission.
It is a custom policy, not equivalent to complete OSMnx walk filtering or proof of actual walkability.

Raw source declared bounds do not provide a uniform external buffer: 125 grids
within1500m of declared edge, including 12 baseline missing-route grids;
four cells have 19298.49m² analysis area outside that bbox. All four have baseline routes.
Declared bounds may differ from retained node extent; no claim is made that external alternative routes are complete.

**Confirmed implementation limitation:** source node/gate access restrictions are not enforced in baseline
way-only filtering. 12413 explicit restricted source nodes; 8465
remain as simplified graph nodes. Conservative sensitivity removes 24370 directed
edges touching/crossing such nodes (5cm vertex-coordinate matching tolerance), fixes every original connector,
and excludes destinations snapped onto forbidden nodes. It yields 407 uncomputed routes,
181 more than baseline. Conditional hours, physical entrances, turn rules,
and one-way-foot restrictions are not fully modeled. This sensitivity is not a newly approved official network.

## 10. Investigation of all 226 missing routes

| kota | missing_cause | n_grid | population |
| --- | --- | --- | --- |
| Kota Jakarta Barat | disconnected_component_without_candidate_park | 22 | 77425.26430001676 |
| Kota Jakarta Pusat | disconnected_component_without_candidate_park | 6 | 15366.39473515749 |
| Kota Jakarta Selatan | disconnected_component_without_candidate_park | 27 | 60231.49463234863 |
| Kota Jakarta Timur | disconnected_component_without_candidate_park | 95 | 185204.8733827311 |
| Kota Jakarta Utara | disconnected_component_without_candidate_park | 76 | 125201.44906824967 |

All 226 origin snaps are in components with **zero snapped candidate park nodes**, even in the full graph.
They occupy 165 components (2–717 nodes; median 4). Full Jakarta resolves zero missing routes.
This establishes a graph/destination-topology cause, not real-world lack of pedestrian/public-park access.
OSM omissions, wrong snap component, or barriers remain possible physical explanations, not confirmed facts.
Boundary distance refers to the whole study perimeter. No separate verified coastline/water mask was
available, so it must not be relabelled coastline distance; coastal location is a visual observation only.
Every affected ID has component IDs/sizes/park counts, snap, boundary distance, canonical/routing city and
original/full distance in `unreachable_grid_diagnostics.csv` and GPKG `unreachable`.
Recommended baseline treatment pending team decision: retain NaN, exclude only in common comparison,
show route uncertainty on map; retain all source rows. Do not replace with0/infinity/1000m or label as confirmed no access.

## 11. Investigation of all 66 far snaps

66 >250m, 17 overlap missing routes. Range
251.48–581.10m, median
316.51m; severity bands 250–500,500–1000,>1000m are diagnostic labels,
not exclusion thresholds. By canonical city: Barat8, Selatan10, Timur26, Utara22, Pusat0.
19 have an edge geometry closer than250m: simplified nearest-node access can
overstate the connector compared with edge-interior snapping. No UTM projection error found.
All cases have origin/node/connector layers; four worst cases have actual road-context panels.
Land ownership, water barriers, missing paths and industrial access were not independently verified.
Recommend flag plus sensitivity; do not automatically delete them or substitute nearest-edge distances
without edge splitting and barrier-aware connector validation.

## 12. Agent1 remote sensing alignment

All2765 IDs, geometry and CRS match exactly. Actual Landsat/DW rasters available; independent exact
coverage-weighted means recomputed for **every grid**, not only a CSV range check: LST within0.001°C,
NDVI within0.0001, DW probabilities within1e-6. Valid LST fractions reproduce within CSV precision.
GEE asset polygon bytes were unavailable: exact equality of that remote asset itself was not established;
local raster support/geometry/means are verified. See `raster_grid_alignment.csv` and eastern coverage layer.

`JKT_R037_C062`: Jakarta Timur, area0.024223111km², LST valid fraction0.277592,
`partial_lst;edge_cell`, population267.129944. Values are DELIVERED. Agent3's provisional50% threshold
excludes it; lowering to25% would give2539 eligible instead of2538 (threshold not changed).
Dynamic World probability and area fractions remain separate: class fractions stay unknown while the
modal-label export is absent. This is Agent1's documented upstream gap, not a GIS join failure.

## 13. Agent3 model maps and spatial assumptions

Frozen Agent3 loader, cleaning and M1–M4 engine rerun in memory on real input; source values,
eligibility, all original scores/ranks and city summaries reproduce. GIS map has all2765 master geometries,
EPSG32748 and correct canonical city assignments. It is intentionally a compact map schema; separate
age fields are verified in merged inputs, combined age count in map where present.
Queen adjacency uses actual clipped polygons,20,988 directed neighbor pairs; no neighbor outside adjacent
lattice positions. Model-map geometry and master table ordering are identical. Islands/eligible-set holes
remain Agent3 statistical decisions; no rewrite of their spatial-statistics engine occurred.
M1–M4 shared population is2538 =2765−226−1, and the two excluded sets have intersection0.
Input completeness is2765 and model eligibility2538. No missing-data delivery failure is attributed to Agent1.

## 14. Integrated outputs and contract

`data/processed/final_model_features.csv`: exactly one full source row per master grid, master order,
all original demographics/distances plus Agent1 raw features and explained QA. Source-integrated companion
to Agent3's official `merged_grid.csv`, not a conflicting replacement engine or formula. Baseline fields
are unchanged. `model_eligible_agent3_baseline` is separate from `input_delivery_complete`.
`park_within_500m_known`/`park_within_1000m_known` are NaN for unknown routes; original0/1 flags remain
for backward compatibility. No eligibility flag silently deletes source rows.
QA geometry counterpart: `outputs/qa/agent2/final_model_features.gpkg` (EPSG32748).
Approved production engine integration should retain Agent3's loader and this documented alias mapping;
this Agent2 worktree's older root `jhim/` was not replaced or merged without authorization.

## 15. Tests and actual outcomes

| stage | checks | failures |
| --- | --- | --- |
| checks_geography | 22 | 0 |
| checks_integration | 40 | 0 |
| checks_network | 29 | 0 |
| checks_parks | 8 | 0 |
| checks_population | 19 | 0 |
| checks_raster | 20 | 0 |
| checks_visual | 6 | 0 |


Commands run from Agent2 using its Python3.12 venv:

```powershell
.venv/Scripts/python scripts/07_integrate_spatial.py --output outputs/qa/agent2/spatial_features_rebuilt.csv
.venv/Scripts/python scripts/agent2_gis.py --stage geography
.venv/Scripts/python scripts/agent2_gis.py --stage population
.venv/Scripts/python scripts/agent2_gis.py --stage parks
.venv/Scripts/python scripts/agent2_gis.py --stage network
.venv/Scripts/python scripts/agent2_gis.py --stage raster
.venv/Scripts/python scripts/agent2_enrich_evidence.py
.venv/Scripts/python scripts/agent2_node_restrictions.py
.venv/Scripts/python scripts/agent2_gis.py --stage integration
.venv/Scripts/python scripts/agent2_gis.py --stage visual
.venv/Scripts/python -m pytest tests/test_agent2_gis.py tests/test_walking_pipeline.py -q --junitxml=outputs/qa/agent2/pytest_results.xml
git diff --check
```

Pytest's actual final count is recorded in `pytest_results.xml` and `validation_summary.json`.
The ten preexisting walking tests also passed independently. Model dry run means all M1–M4 scores/ranks
rerun using frozen Agent3 source; full Moran permutations/dashboard AppTests were not rerun because
official baseline inputs/formulas/results were unchanged. Agent3's own earlier test claims are not
substituted for Agent2's independent tests. During implementation a diagnostic initially assumed age
columns existed in the compact GIS export; that assumption was repaired and final integration rerun.
Initial exploratory centroid reads were corrected to boundless windows before final hybrid checks.
Final tests do not weaken any failed scientific condition; source limitations remain registered.

## 16. Geographical model robustness and visual evidence

| scenario | fixed_common_population | n_valid | comparison_baseline_n_valid | m4_top_jaccard | m4_rank_spearman_intersection |
| --- | --- | --- | --- | --- | --- |
| full_jakarta_network | False | 2538 | 2538 | 1.0 | 1.0 |
| full_jakarta_network | True | 2538 | 2538 | 1.0 | 1.0 |
| straight_line_polygon | False | 2764 | 2538 | 0.534682 | 0.946431 |
| straight_line_polygon | True | 2538 | 2538 | 0.558282 | 0.94986 |
| straight_line_representative_point | False | 2764 | 2538 | 0.561765 | 0.952897 |
| straight_line_representative_point | True | 2538 | 2538 | 0.5875 | 0.956082 |
| positive_access_tags_only | False | 2523 | 2538 | 0.420168 | 0.895987 |
| positive_access_tags_only | True | 2523 | 2523 | 0.421348 | 0.897684 |
| explicit_node_restrictions | False | 2357 | 2538 | 0.842105 | 0.992759 |
| explicit_node_restrictions | True | 2357 | 2357 | 0.895582 | 0.992698 |
| fractional_population_aggregation | False | 2538 | 2538 | 0.874539 | 0.997828 |
| fractional_population_aggregation | True | 2538 | 2538 | 0.874539 | 0.997828 |
| exclude_age_source_no_support | False | 2526 | 2538 | 0.988235 | 0.999941 |
| exclude_age_source_no_support | True | 2526 | 2526 | 1.0 | 1.0 |


Fixed-common-population comparisons recompute BOTH baseline and alternative rankings on their exact
intersection, to separate input definition from changed eligibility. Unfixed comparisons retain the original
baseline, report eligibility changes, and therefore combine measurement and selection effects.
All scenarios use unchanged provisional Agent3 formulas/weights. Network-vs-straight-line differences
are specification differences, not universal proof that modeled network distance is empirically more accurate.
Full Jakarta changes9 known distances by >1m (largest reduction59.925m) but resolves no missing routes;
all affected M4 distances are saturated at1km, so M4 scores/ranks and top254 do not change.
Straight-line polygon distance within500m covers1526 cells vs537 network cells.

Actual rendered PNGs were opened and visually inspected with the image viewer: `gis_review_atlas.png`
(LST,NDVI,population,ages,distance,missingness,M1–M4,rank gain,full-network), `network_edge_qa_map.png`,
`far_snap_sample_details.png`, `lisa_m4_qa.png`; an eastern raster coverage detail is supplied separately.
No gross geographic shift or missing model geometry found. Missing routes concentrate at coastal/northern
and eastern/southern pockets; age-count spatial pattern closely follows population. Far-snap sample
R024_C047 shows a nearby edge interior despite a long nearest-node connector; R056_C000 is a narrow
clipped cell, and other examples show sparse retained graph geometry. These are visual/topological
observations, not verified land-use or actual pedestrian-barrier classifications.
QGIS3.44.15 is installed; standalone PyQGIS created `qgis/agent2_gis_qa.qgz` with21 valid layers,
including read-only road context from the main repository. Diagnostic/model/raster groups start hidden.
No interactive QGIS GUI session or field validation is claimed. Project creation is not numerical validation.

## 17. Remaining limitations and decisions

Temporal mismatch2024 temperature/demography vs2026 OSM; no verified gate inventory/public park census;
node restrictions and conditional access not enforced in official baseline; lack of uniform external buffer;
centroid/nearest-node proxy; age raster support zeros; hybrid population boundary allocation; partial cells;
boundary release provenance incomplete; inaccessible GEE asset bytes; DW label fractions absent;
provisional weights/vulnerability construct. See issue log and ten-question decision register.
No health causality, air temperature, physiological heat stress or mortality validation is claimed.

## 18. Independent auditor instructions

1. Inspect `baseline/capture.json` and manifest hashes; distinguish committed Agent1 from provisional Agent3.
2. Verify source availability in main repo; do not regenerate/download GraphML merely because worktree lacks it.
3. Run strict integration and QA stages; review every `checks_*.json`, not only passing test counts.
4. Trace all226 IDs to component/park evidence and all66 snaps to point/node/edge layers; inspect original
   park IDs and source tag policy. Do not interpret missing routing as confirmed no access.
5. Review node-restriction and access-tag scenarios, exact common-set comparisons, and2026 OSM scope.
6. Validate raster support around JKT_R037_C062 and19 age-no-support cells.
7. Compare full source table to Agent3 merged loader; verify original2538 eligibility, city summaries and maps.
8. Decide the research policies before accepting any official revised ranking; independently audit scientific
   conclusions and manuscript claims. This handover supplies counter-evidence as well as supporting evidence.

## 19. Reproduction and environment

Pinned environment `requirements-agent2.txt`. Fresh Python3.12:

```powershell
py -3.12 -m venv .venv
.venv/Scripts/python -m pip install -r requirements-agent2.txt
# Use the delivered immutable baseline; capture once only if starting a NEW baseline.
.venv/Scripts/python scripts/agent2_gis.py --stage geography
.venv/Scripts/python scripts/agent2_gis.py --stage population
.venv/Scripts/python scripts/agent2_gis.py --stage parks
.venv/Scripts/python scripts/agent2_gis.py --stage network
.venv/Scripts/python scripts/agent2_gis.py --stage raster
.venv/Scripts/python scripts/agent2_enrich_evidence.py
.venv/Scripts/python scripts/agent2_node_restrictions.py
.venv/Scripts/python scripts/agent2_gis.py --stage integration
.venv/Scripts/python scripts/agent2_gis.py --stage visual
.venv/Scripts/python -m pytest tests/test_agent2_gis.py tests/test_walking_pipeline.py -q
& 'C:/Program Files/QGIS 3.44.15/bin/python-qgis-ltr.bat' scripts/agent2_qgis_project.py
.venv/Scripts/python scripts/agent2_write_handoff.py
```

`--source-root` on `agent2_gis.py` can locate read-only baseline data elsewhere. Supplementary evidence
scripts currently expect sibling `jakarta-heat`; update the single documented SOURCE constant if relocating.
`--stage all` runs core stages only; node sensitivity is run after core network and before final integration.
No shell environment variables are required; upstream inputs are the frozen snapshots. Primary-document
retrieval is small and can fail without blocking local evidence regeneration. QGIS is optional for numerical QA.

## 20. Final readiness assessment

Person2 engineering, source integration, route diagnostics and reproducible auditor package are delivered.
All available source rows preserved; unknown routes not imputed; independent geography and raster evidence
recorded; baseline model scores/maps reconciled; material alternatives quantified. **DONE WITH DOCUMENTED
LIMITATIONS**, not scientifically final. Methodology sign-off, historical OSM alignment or explicit mixed-year
framing, public/gate validation and independent scientific audit remain research-team work.

## 21. Remediation checkpoint — 20 November 2026

The previous DONE statement describes the earlier engineering handover, not
closure of the independent audit. Seven Agent2 P1 issues are now under active
remediation. Read `REMEDIATION_AGENT2.md` and
`CONTINUE_AGENT2_REMEDIATION_PROMPT.md` for the authoritative current checkpoint.
Buffered real age rasters recover13 original source-support gaps; six total/age
cells remain analytical null in separately versioned corrected outputs. Proposed
common eligibility becomes2536, while the original2538 baseline is preserved.
Park/public entrance and physical connector claims remain unverified. Latest
post-test source changes and full reproduction/integration checks are pending.
Work stopped at the user's request for agent transfer; the sprint is not complete.
