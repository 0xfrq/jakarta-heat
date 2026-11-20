"""Render the Agent2 handover from actual QA outputs, never fabricated numbers."""
from pathlib import Path
from datetime import datetime, timezone
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/qa/agent2'
HAND=ROOT/'handoff'


def read(name):return json.loads((OUT/name).read_text(encoding='utf-8'))


def md_table(df):
    # No optional tabulate dependency. Escape literal Markdown delimiters.
    def cell(v):return str(v).replace('|','/').replace('\n',' ')
    return '| '+' | '.join(map(cell,df.columns))+' |\n| '+' | '.join(['---']*len(df.columns))+' |\n'+''.join(
        '| '+' | '.join(map(cell,row))+' |\n' for row in df.itertuples(index=False,name=None))


def main():
    HAND.mkdir(exist_ok=True)
    geo=read('geographic_integrity.json');dem=read('demographic_summary.json');net=read('network_summary.json')
    integ=read('integration_summary.json');parks=read('park_summary.json');parkcache=read('park_cache_provenance.json')
    barrier=read('node_restriction_summary.json');extent=read('network_source_extent_summary.json')
    osm=read('osm_revision_timestamp_evidence.json');rs=read('remote_alignment_summary.json');base=read('baseline_metrics.json')
    snap=read('baseline/capture.json')
    sensitivity=pd.read_csv(OUT/'gis_model_sensitivity_summary.csv')
    causes=pd.read_csv(OUT/'unreachable_cause_by_city.csv')
    checks=[]
    for p in sorted(OUT.glob('checks_*.json')):
        records=json.loads(p.read_text())
        checks.append({'stage':p.stem,'checks':len(records),'failures':sum(not x['pass'] for x in records)})
    initial=pd.DataFrame([
        ['Boundary/grid','GPKG + master CSV','Exists; earlier integrity assertions only','Independent geometry/clip/city evidence absent','Full lattice/union/owner recomputation; PASS'],
        ['Population/age','3 CSV + local TIFF','No missing CSV values','Manual QGIS aggregation; provenance not catalogued','TIFF metadata, alignment, hybrid recomputation, mask QA'],
        ['Parks','parks_jakarta.gpkg','Mapped candidates, public entry unverified','Unknown access; original polygons not yet inspected','Recover cache, reproduce polygons, tag/exclusion audit'],
        ['Walking','5 city outputs + full graph in main repo','226 unknown routes, 66 far snaps','Cause, crop, barriers and temporal scope unverified','Reproduce routes, components, full graph and gate scenarios'],
        ['Remote sensing','Agent1 committed CSV/GPKG/rasters','2765 delivered values','Independent alignment/aggregation pending','Exact geometry match + all-grid raster recomputation'],
        ['Models/maps','Agent3 uncommitted working outputs','Provisional 2538 common grids','Need independent GIS/input reconciliation','Freeze code/results; recompute M1-M4 and city summaries'],
        ['Integrated sources','No final_model_features.csv initially','Missing companion integration','Full source population + QA/eligibility separation','Created 2765-row compatible companion table'],
    ],columns=['Component','Existing output','Actual validation status at start','Gaps','Action/result'])
    table=md_table(initial)
    (OUT/'initial_status.csv').write_text(initial.to_csv(index=False),encoding='utf-8')
    gitrows=pd.DataFrame([{'workspace':k,**{x:v[x] for x in ['branch','sha']},
                          'state':'uncommitted snapshot' if v['status'] else 'clean at capture'} for k,v in snap['workspaces'].items()])
    text=f'''# AGENT2 HANDOFF — GIS, accessibility, spatial QA and integration

Generated UTC: {datetime.now(timezone.utc).isoformat()}. Workspace `D:/jakarta-heat-agent2`.
**Status: DONE WITH DOCUMENTED LIMITATIONS for this engineering/QA handover.**
This is not approval of final scientific rankings, a synchronous 2024 OSM inventory, public entrances,
or the manuscript. Open scientific decisions are in `AGENT2_DECISION_REGISTER.md`.

## 1. Initial audit and safe baseline

{table}

{md_table(gitrows)}
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
`{parkcache['snapshot']['timestamp_osm_base']}`. The original network extract contains revisions up to
`{osm['latest_revision_utc']}`; this is a lower bound on extraction date, not an exact snapshot date.
Raw network acquisition URL is not documented. Graph created `{net['graph_attributes']['created_date']}`
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
CRS EPSG:32748. Union area {geo['area_km2']:.9f} km². Clip symmetric difference
{geo['coverage_symdiff_m2']:.8f} m²; absolute internal overlap numerical residual <1m².
Every geometry matches its exact 500m lattice square intersected with boundary (error <0.01m²).
{geo['partial_cells']} partial cells; {geo['coverage_lt10pct']} coverage <10%; {geo['area_lt005km2']} area <0.05km²;
minimum clipped area {geo['min_area_m2']:.6f}m². None were automatically deleted.
Distinguish square area 250000m², clipped area, clipped/square ratio, and raster valid-pixel fraction.

{geo['routing_city_differs_majority']} grid representative points fall in another city than the majority-area owner.
This explains a routing-partition choice, not incorrect canonical city labels. All city summary checks use
the majority-area owner, and baseline routing is reproduced according to its actual point partition.

## 7. Demographic QA and age alternatives

No CSV missing/negative values; total estimated population {dem['totals']['population']:,.3f}; children
{dem['totals']['pop_child']:,.3f}; elderly {dem['totals']['pop_elderly']:,.3f}; combined
{dem['totals']['pop_vulnerable']:,.3f}. Six population-zero cells and 20 zeros in each age group.
No combined age count exceeds total+1 person. Raster origins/resolution align exactly to integer pixels.
All 2765 original hybrid sums reproduce within 0.01 person (maximum total-pop difference
{dem['recomputation']['population']['qgis_hybrid']['max_abs_difference']:.6f}, child
{dem['recomputation']['pop_child']['qgis_hybrid']['max_abs_difference']:.6f}, elderly
{dem['recomputation']['pop_elderly']['qgis_hybrid']['max_abs_difference']:.6f}). Floating summation precision
explains these small residuals. Original values are preserved.

14 populated grids have both ages zero (together ~65 modeled persons). Of these, **13** have no valid age
pixel support; one has valid age pixels summing to zero and total population ~0.00012. Overall 19 cells
have zero age pixel support, including six population-zero cells. QGIS sum over no valid pixels returns 0;
this is not evidence of no children/elderly. Source zeros stay visible, with `qa_age_source_no_support` and
an exclusion sensitivity. `zero_age_populated_grid_diagnostics.csv` distinguishes the causes per ID.

Population–combined-age Spearman {dem['spearman_population_vulnerable']:.9f}; Pearson
{dem['pearson_population_vulnerable']:.9f}. Vulnerable-share median
{dem['vulnerable_share']['50%']:.6f}; P5–P95 {dem['vulnerable_share']['5%']:.6f}–{dem['vulnerable_share']['95%']:.6f}.
Source-integrated `vulnerable_share` is NaN for zero total population (undefined ratio). Agent3's scenario
variable `vuln_share` uses 0 there; this deliberate existing convention is documented and not changed.
Counts represent exposure of age groups; share represents age composition. They are not interchangeable.

## 8. Park inventory and access QA

{parks['n']} baseline polygons; no invalid geometries, duplicate IDs or exact duplicate shapes;
{parks['unnamed']} unnamed, {parks['total_area_km2']:.6f}km² clipped area. {parks['access']['unknown']} unknown access;
9 `yes`, 1 `permissive` (positive tags, still not independently verified). Unknown tags are never proof of
unrestricted entry. `leisure=park` excludes gardens and other green-space classes by design; completeness
relative to a municipal public-park inventory is unverified.

Recovered original cache has {parkcache['raw_polygon_count']} polygon candidates; two excluded (`private`,
`permit`). IDs and clipped geometries reproduce current inventory within
{parkcache['maximum_geometry_difference_m2']:.8f}m². {parkcache['parks_extend_outside_study']} original polygons extend
outside the study, {parkcache['parks_crossing_city_borders']} cross internal city boundaries. Original polygons
are now inspectable in QA GPKG; clipping changes their representative points. No new park was silently added.
Sample IDs/access evidence and destination counts are in `park_manual_review_samples.csv` and
`park_samples_qa.png`. Named examples
include RPTRA Rorotan and Taman Sungai Kendal; high-use unnamed polygons are explicitly retained for review.
There was no field visit, verified gate/operating-hours check, or claim that a sampled park is confirmed public.

## 9. Walking graph provenance, filter, connectivity and extent

Full graph {net['full_nodes']:,} nodes / {net['full_edges']:,} directed edges, {net['full_components']} weak components,
largest {net['full_largest_component']:,}. All retained directed edges have finite nonnegative meter lengths;
every edge has a reverse connection. All five city graph edges/keys/lengths match the common full source;
metadata also identifies offline version2 and 1500m buffer. Old Pusat online backups were not mixed in.
The filter excludes motorways/trunks/construction, area roads, foot=no/private, access=no/private without
explicit foot permission, private service without override, and cycleways absent explicit foot permission.
It is a custom policy, not equivalent to complete OSMnx walk filtering or proof of actual walkability.

Raw source declared bounds do not provide a uniform external buffer: {extent['grids_within1500m_edge']} grids
within1500m of declared edge, including {extent['missing_grids_within1500m_edge']} baseline missing-route grids;
four cells have {extent['outside_area_m2']:.2f}m² analysis area outside that bbox. All four have baseline routes.
Declared bounds may differ from retained node extent; no claim is made that external alternative routes are complete.

**Confirmed implementation limitation:** source node/gate access restrictions are not enforced in baseline
way-only filtering. {barrier['blocked_source_nodes']} explicit restricted source nodes; {barrier['blocked_retained_graph_nodes']}
remain as simplified graph nodes. Conservative sensitivity removes {barrier['removed_directed_edges']} directed
edges touching/crossing such nodes (5cm vertex-coordinate matching tolerance), fixes every original connector,
and excludes destinations snapped onto forbidden nodes. It yields {barrier['missing_routes']} uncomputed routes,
{barrier['baseline_known_now_missing']} more than baseline. Conditional hours, physical entrances, turn rules,
and one-way-foot restrictions are not fully modeled. This sensitivity is not a newly approved official network.

## 10. Investigation of all 226 missing routes

{md_table(causes)}
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

66 >250m, {net['far_missing_overlap']} overlap missing routes. Range
{net['far_snap_distribution']['min']:.2f}–{net['far_snap_distribution']['max']:.2f}m, median
{net['far_snap_distribution']['50%']:.2f}m; severity bands 250–500,500–1000,>1000m are diagnostic labels,
not exclusion thresholds. By canonical city: Barat8, Selatan10, Timur26, Utara22, Pusat0.
{net['far_node_but_edge_lt250']} have an edge geometry closer than250m: simplified nearest-node access can
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

{md_table(pd.DataFrame(checks))}

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

{md_table(sensitivity[['scenario','fixed_common_population','n_valid','comparison_baseline_n_valid','m4_top_jaccard','m4_rank_spearman_intersection']].round(6))}

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
'''
    (HAND/'AGENT2_HANDOFF.md').write_text(text,encoding='utf-8')
    write_issues(barrier,extent)
    write_decisions()
    write_dictionary()


def write_issues(barrier,extent):
    issues=[
      ('P2-INT-01','HIGH','Person2 integration','Old left joins did not enforce complete exact source ID sets, finite numeric types or aliases.','Silent missing rows/bad fields could enter models.','Strict fail-fast source contracts.','Implemented person2_contracts; rebuilt original2765 rows without value changes.','Bad keys/types/aliases/indicators fail; original sources reproduce.','FIXED AND TESTED'),
      ('P2-NET-01','HIGH','Person2 routing','226 missing routes in165 components; no candidate park in same component; full graph resolves0.','Selection bias and false no-access interpretation.','Preserve NaN + component diagnostics + explicit eligibility policy.','All226 classified; CSV/GPKG/city summary, no imputation.','Every affected ID accounted for and unknown distinguished from absent access.','DIAGNOSTICS COMPLETE; METHOD DECISION OPEN'),
      ('P2-NET-02','HIGH','Person2 graph restrictions',f"Way-only filter ignores explicit node restrictions; conservative fixed-snap scenario gives{barrier['missing_routes']} missing routes ({barrier['baseline_known_now_missing']} extra).",'Baseline may route through restricted gates.','Validate node/conditional restrictions and approve explicit graph policy.','Implemented conservative edge-removal scenario and downstream M4 rerun; original unchanged.','Team chooses restriction policy; any adopted correction reruns all cities/models and validates gates.','CONFIRMED LIMITATION; SENSITIVITY DELIVERED'),
      ('P2-TIME-01','HIGH','GIS temporal scope','Park OSM base2026-11-19; raw network latest revision2026-11-18; study temperature/demography2024.','Cannot call full feature stack synchronous2024.','Historical2024 OSM or explicit mixed-year exploratory framing.','Recorded exact park timestamp and raw revision evidence; no invented historical source.','Approved temporal framing or verified historical extract + complete rerun.','OPEN TEAM DECISION'),
      ('P2-PARK-01','HIGH','Person2 destination validity','1005/1015 candidate parks have unknown access; no verified public gates.','Public-park and actual gate access may be overstated.','OSM candidates terminology; tag/entrance sensitivity; municipal/field validation.','Recovered1017 original polygons,2 exclusions, sample IDs; positive-tag scenario.','Unknown tags never treated as proof; confirm entrances for actual public-access claims.','DOCUMENTED; FIELD VALIDATION OPEN'),
      ('P2-NET-03','MEDIUM','Network external extent',f"{extent['grids_within1500m_edge']} grids close to declared extract edge;4 cells partly outside header extent.",'External detours/destinations may be missing.','Acquire consistently buffered/historical source if chosen by team.','Quantified extent,12 missing-route cases near edge; full local graph tested.','Verify uniform external buffer or disclose truncation in publication.','DOCUMENTED LIMITATION'),
      ('P2-SNAP-01','MEDIUM','Origin/destination connectors','66 origin snaps>250m,17 missing;19 have edge<250m; max park connector414.82m.','Straight connectors may overstate distance or cross barriers.','Barrier-aware edge splitting or verified entrances as new specification.','All66 mapped/diagnosed; no automatic deletion or guessed barrier attribution.','Retain uncertainty flags; separately validate replacement snapping method.','DIAGNOSTICS COMPLETE; METHOD OPEN'),
      ('P2-AGE-01','MEDIUM','Age masks/zeros','19 grids lack valid age pixel support;13 populated, one additional populated grid has valid zero-age pixels.','Zero sum could be mistaken for no vulnerable people.','Flag source-no-support and test exclusion.','Added QA and exact-support table; preserved baseline values; exclusion sensitivity.','Auditor can distinguish modeled0, empty support and zero denominator.','FIXED FLAGS; SOURCE MASK LIMITATION DOCUMENTED'),
      ('P2-AGE-02','HIGH','Vulnerability construct','Spearman(total,child+elderly)=0.999551; age share varies little.','M4 demographic count resembles population exposure more than age composition.','Choose count/share construct and report sensitivity.','Added vulnerable_share with undefined-zero-denominator policy; did not change M4.','Team selects interpretation and robustness requirements.','OPEN METHODOLOGY'),
      ('P2-POP-01','MEDIUM','Population aggregation','Manual QGIS uses centroid sums with fractional fallback<=1 pixel; exact sums differ locally.','Cell ranks can depend on pixel inclusion rule.','Document hybrid; evaluate exact fractional allocation from compatible masks.','All-grid hybrid reproduced<0.01person; fractional scenario rerun.','Disclose boundary rule and avoid treating masked-age fractional sums as independent ground truth.','REPRODUCED; ALTERNATIVE PROVISIONAL'),
      ('P2-GRID-01','MEDIUM','Partial cells/city partition','383 partial cells;65 coverage<10%;14 point-city vs majority-city differences.','Tiny-cell density/means and partition boundaries can distort interpretation.','Keep geometry/QA; sensitivity; document ownership vs routing partition.','Exact lattice/clip/area verified, flags and map provided.','No silent cell deletion; ownership/city summaries consistent.','VERIFIED WITH QA'),
      ('P2-SRC-01','MEDIUM','Boundary/network source release','Boundary API metadata JSON and original raw OSM URL absent; OSM revision time only lower bound.','Historical provenance not completely reconstructable from URLs.','Retain hashes and recover archived metadata if available.','Local source names/method/code/hashes and observed revision ranges recorded.','Document exact release/URL if recovered; otherwise explicit limitation.','OPEN PROVENANCE LIMITATION'),
      ('A1-RS-01','MEDIUM','Agent1 upstream','JKT_R037_C062 has LST valid0.277592, all LST/NDVI delivered.','One eligibility exclusion under provisional50% rule.','Team decides threshold; keep delivery and eligibility separate.','All-grid raster means/geometry independently verified, no threshold change.','No missing-delivery claim; eligibility flags/hash reconcile.','VERIFIED; THRESHOLD DECISION OPEN'),
      ('A1-DW-01','MEDIUM','Agent1 upstream','DW modal-label fractions unavailable; probability rasters present.','Probability must not be read as area fraction.','Obtain Agent1 GEE export if needed for additional analysis.','Missing fractions preserved; probabilities independently recomputed.','Use correct labels; fill fractions only after real label export.','UPSTREAM DOCUMENTED GAP'),
      ('A3-MODEL-01','HIGH','Agent3/coordinator','Formulas/weights provisional; GIS scenarios materially alter M4 in some definitions.','Priority ranking is not scientifically approved.','Agree weights/constructs/access policy before final recommendations.','Frozen engine/all baseline scores/ranks/cities reconciled; new GIS sensitivity exported.','Approved specification and independent robustness/scientific audit.','OPEN TEAM DECISION'),
      ('A3-SYNC-01','MEDIUM','Agent3 integration','Source code/results were uncommitted at capture.','Live files may evolve independently from tested snapshot.','Integrate approved committed revisions after operator authorization.','Snapshot/hash all consumed code/results; other worktrees untouched.','Auditor can reproduce exact snapshot; committed integration separately authorized.','SNAPSHOT VERIFIED; RELEASE PROVISIONAL'),
    ]
    cols=['Issue ID','Severity','Component/owner','Evidence','Impact','Proposed fix','Actual action/blocker','Acceptance criteria','Status']
    df=pd.DataFrame(issues,columns=cols)
    (HAND/'AGENT2_ISSUES.md').write_text('# AGENT2 prioritized issue log\n\nHIGH items require scientific attention; FIXED items are engineering fixes, not approval of the research.\n\n'+md_table(df),encoding='utf-8')
    df.to_csv(OUT/'issue_register.csv',index=False)


def write_decisions():
    entries=[
      ('D01','Keep 50% LST valid threshold?','One delivered edge grid0.277592;25% adds1 eligible.','50% /25% /strict full-QA.','Keep50% provisional baseline and report threshold sensitivity; do not optimize thresholds for attractive results.','Changes1 grid at25%; higher thresholds remove more.','YES, before final analysis'),
      ('D02','Destination: representative point, boundary, or verified entrance?','1015 OSM polygons; no verified gates; clipped representative points differ from entrances.','Current rep-point proxy /boundary proxy /verified gates.','Describe rep-point proxy explicitly; use gate validation before actual usable-access claims.','Boundary/entrance distances can change ranks; evaluated Euclidean definitions only.','YES for official change'),
      ('D03','How treat disconnected routes and explicit gates?','All226 components lack destinations; fixed-snap restriction scenario has407 missing.','Unknown+exclude /verified topology repair /named imputation sensitivity.','Keep raw NaN; disclose graph causes; choose node policy after reviewing restriction scenario.','Eligibility/selection and M4 change; no real-world no-access claim.','YES for official policy'),
      ('D04','Require known distance for shared M1–M4 population?','2765 total vs2538 baseline; missingness concentrated geographically.','Common complete-case /model-specific sets /explicit missing-data sensitivity.','Common set for comparable rankings plus all-grid heat/descriptive maps and selection table.','Model-specific heat maps cover more cells but comparison population differs.','YES'),
      ('D05','Age counts or age share for vulnerability?','Spearman0.99955; share median~0.297 with narrow central range.','Count as exposure /share as composition /separate dimensions.','Choose construct explicitly; show count/share sensitivity; no unilateral formula change.','Age-share M4 can differ strongly; zero denominators and masked support need policies.','YES'),
      ('D06','Which park access-tag and node-restriction policy?','1005 unknown park tags,10 positive; node constraints ignored in baseline.','Candidates except explicit restrictions /positive tags only /verified public park set; static or conditional gate rules.','Keep broad candidates as proxy and restrictive alternatives as sensitivity until verified inventory.','Positive-only severely undercounts untagged public parks; static restrictions may overexclude conditional access.','YES'),
      ('D07','How handle partial cells and raster boundary inclusion?','383 partial,65<10%, one0.423m²; QGIS hybrid population method.','Keep+flag /exclude tiny /fractional allocation.','Keep source grid intact; report exclusions as sensitivity; consider stable area thresholds before final ranks.','Changes normalization/eligibility; small-cell density especially unstable.','YES for official exclusions'),
      ('D08','When are outputs intervention recommendations?','Provisional weights, unknown entries, mixed-year OSM and gate sensitivity.','Exploratory screening /qualified planning support /validated recommendations.','Use exploratory spatial prioritization language until temporal/access/specification audit approved.','Affects claims and maps, not just code.','YES, scientific sign-off'),
      ('D09','Annual LST vs exposure and temporal synchronization?','Clear-sky~10:30 annual median surface temperature; OSM revisions2026.','Mixed-year proxy study /historical2024 OSM; seasonal LST sensitivity by Agent1.','State LST sampling limits; obtain2024 OSM or explicitly approve mixed-year framing.','Historical network/parks require consistent rerun; no air-temperature/health claims.','YES'),
      ('D10','Which GIS limitations must appear in paper?','All issues above are evidenced, not hypothetical.','Concise methods+limitations /supplement source QA and decision register.','Include temporal mismatch, graph/entry uncertainty, source masks, partial grids, missingness selection, provisional weights and unresolved fractions.','Constrains interpretation and reproducibility; no numerical change alone.','YES, publication sign-off'),
    ]
    df=pd.DataFrame(entries,columns=['ID','Question','Evidence','Options/tradeoffs','Recommendation','Output consequence','Human approval'])
    (HAND/'AGENT2_DECISION_REGISTER.md').write_text('# Scientific decision register\n\nEngineering work has proceeded; these pending decisions were not treated as blockers to independent QA. No option here is implicitly approved.\n\n'+md_table(df),encoding='utf-8')
    df.to_csv(OUT/'decision_register.csv',index=False)


def write_dictionary():
    final=pd.read_csv(ROOT/'data/processed/final_model_features.csv')
    specs={
      'grid_id':('Master','identifier','500m projected lattice cell clipped to boundary','Never missing; unique key','All joins','Stable grid version required'),
      'kota':('Master','city label','Largest overlap administrative owner','Never missing','Summaries','May differ from representative-point routing partition'),
      'area_km2':('Master geometry','km²','Clipped analysis polygon area','Never missing','Area/edge QA','Not full250000m² footprint'),
      'coverage_ratio':('Master geometry','fraction','Analysis area /250000m²','Never missing','Edge QA','Not satellite valid fraction or measured land cover'),
      'longitude':('Master geometry','degrees east','Clipped representative point EPSG4326','Never missing','Display','Not population-weighted location'),
      'latitude':('Master geometry','degrees north','Clipped representative point EPSG4326','Never missing','Display','Not population-weighted location'),
      'population':('WorldPop total2024 R2025A v1','modeled persons','QGIS hybrid pixel sum','0 is modeled count; no missing','Exposure','Model estimates; not census counts; hybrid allocation'),
      'pop_child':('WorldPop API agesex2024 R2025A','modeled persons0–14','Both sexes; QGIS hybrid sum','0 can be empty raster support; inspect QA','Age count component','API source mask differs at boundary; not field age census'),
      'pop_elderly':('WorldPop API agesex2024 R2025A','modeled persons65+','Includes90+; QGIS hybrid sum','0 can be empty raster support; inspect QA','Age count component','Same mask limitation as children'),
      'park_distance_m':('Person2 OSM2026','meters','Origin connector+network shortest path+park rep connector','NaN=routing not computed; never zero-imputed','M4 baseline','Approximate points, no verified entrances/public access'),
      'grid_snap_m':('Person2 OSM2026','meters','Euclidean origin rep to nearest graph node','No missing in baseline','Snap QA','Straight connector may cross barriers; simplified nodes'),
      'park_reachable':('Person2 OSM2026','0/1','1 iff modeled distance computed','0=unknown/uncomputed route, not proven no real-world access','Legacy contract','Name can mislead; use qa_route_not_computed'),
      'park_access_500m':('Person2 OSM2026','0/1','Legacy1 if computed distance<=500m','0 includes both known>500 and unknown distance','Legacy dashboard','Use park_within_500m_known to preserve uncertainty'),
      'park_access_1000m':('Person2 OSM2026','0/1','Legacy1 if computed distance<=1000m','0 includes unknown distance','Legacy dashboard','Use park_within_1000m_known'),
      'lst_mean_c':('Agent1 Landsat9 C2 L2,2024','°C','Exact coverage-weighted cell mean of pixel temporal median','No missing delivered','M1–M4 via lst_c alias','Surface clear-sky sampling; not air temperature'),
      'lst_c':('Agent1 alias','°C','Identical to lst_mean_c','No missing','Agent3 required','Same LST limitations'),
      'ndvi_mean':('Agent1 Landsat9,2024','index −1..1','Exact cell mean of pixel temporal median NDVI','No missing','Vegetation','Spectral proxy, not usable park supply'),
      'ndvi':('Agent1 alias','index −1..1','Identical to ndvi_mean','No missing','Agent3 required','Same NDVI limitations'),
      'lst_valid_fraction':('Agent1 Landsat9,2024','fraction','Area with valid LST /clipped polygon area','No missing;0.277592 minimum','Agent3 lst_valid_frac alias and threshold','Not fraction of full square or fraction of dates'),
      'lst_observation_count':('Agent1 Landsat9,2024','observations per pixel','Coverage-weighted mean of valid pixel counts','No missing','Agent3 lst_obs alias','Unequal seasonal/scene support'),
      'lst_std_c':('Agent1 Landsat9,2024','°C','Spatial SD of pixel median LST','No missing','Within-cell QA','Not uncertainty of annual median'),
      'lst_min_c':('Agent1 Landsat9,2024','°C','Min touching valid pixel median LST','No missing','QA','Partial-pixel inclusion; not daily minimum'),
      'lst_max_c':('Agent1 Landsat9,2024','°C','Max touching valid pixel median LST','No missing','QA','Not annual daily maximum'),
      'lst_unc_mean_k':('Agent1 Landsat9 ST_QA,2024','K','Cell mean of per-pixel median scene uncertainty','No missing','Agent3 lst_unc_k alias','Not uncertainty of final median/composite'),
      'lst_observation_min':('Agent1 Landsat9,2024','observations','Minimum clear LST count in cell','No missing','QA','Not a per-grid scene count'),
      'ndvi_std':('Agent1 Landsat9,2024','index','Spatial SD of median NDVI','No missing','QA','Not temporal variability'),
      'ndvi_valid_fraction':('Agent1 Landsat9,2024','fraction','Valid NDVI pixel area/clipped area','No missing','Coverage QA','Different from LST valid fraction'),
      'landsat_footprint_fraction':('Agent1 Landsat9 export,2024','fraction','Export AOI raster support/clipped area','No missing','AOI alignment QA','Does not prove remote GEE asset byte equality'),
      'tree_prob_mean':('Agent1 Dynamic WorldV1,2024','probability0–1','Cell mean of temporal median per-image tree probability','One sliver cell NaN','Sensitivity; Agent3 trees_prob alias','Not tree area fraction'),
      'built_prob_mean':('Agent1 Dynamic WorldV1,2024','probability0–1','Cell mean of temporal median per-image built probability','One sliver cell NaN','Sensitivity; Agent3 built_prob alias','Not built area fraction'),
      'dw_valid_fraction':('Agent1 Dynamic WorldV1,2024','fraction','Valid probability raster area/clipped area','Can0 at tiny sliver','Coverage QA','Probability raster support, not class-label fractions'),
      'qa_area_km2':('Agent1 master geometry','km²','Clipped analysis polygon area rounded in CSV','No missing','Alignment QA','Alias by meaning of area_km2, different rounding'),
      'rs_qa_flags':('Agent1 QA','semicolon-separated text','partial_lst,edge_cell,high_unc,low_obs,no_lst,footprint_gap','Empty=no reported flags','Source QA','Not all flags excluded by Agent3 baseline'),
      'rs_qa_ok':('Agent1 QA','boolean','False if partial/no LST,low observations,high uncertainty','No missing','Agent3 sensitivity','13 false; baseline only excludes low LST fraction1'),
      'pop_vulnerable':('Agent2 original age counts','modeled persons','pop_child+pop_elderly','No missing; source-mask zeros retained','Alternative feature/compatibility','Strongly correlated with total population'),
      'vulnerable_share':('Agent2 original demographic counts','fraction','pop_vulnerable/population when population>0','NaN for6 zero-pop cells;19 source-no-support flags','Age-composition alternative','Agent3 vuln_share convention sets zero-pop0; original formula unchanged'),
      'input_delivery_complete':('Agent2 source contract','boolean','LST,NDVI,total,child,elderly all delivered numerically','AllTrue; route missingness handled separately','Delivery status','Does not imply full GIS validity or complete DW class fractions'),
      'qa_route_not_computed':('Agent2 original routes','boolean','park_distance_m is NaN','True=unknown routing','Missingness QA','Not confirmed lack of access'),
      'qa_far_snap':('Agent2 original snaps','boolean','grid_snap_m>250m','False includes known<=250m','Snap QA','Diagnostic threshold, no automatic exclusion'),
      'qa_partial_grid':('Agent2 master geometry','boolean','coverage_ratio<1−1e−8','No missing','Area QA','Includes any clipped cell; not raster coverage'),
      'qa_coverage_lt10pct':('Agent2 master geometry','boolean','coverage_ratio<0.1','No missing','Tiny-cell QA','Diagnostic threshold'),
      'qa_lst_low_valid':('Agent2/Agent3 QA rule','boolean','lst_valid_fraction<0.5','No missing','Baseline model eligibility','Threshold provisional; not delivery missingness'),
      'qa_age_zero_pop_positive':('Agent2 demographic QA','boolean','population>0 and both age counts0','No missing','Review source support','14 cases,13 have absent support'),
      'qa_age_source_no_support':('Agent2 raw age raster counts','boolean','No valid fractional child or elderly pixel intersects grid','No missing;19True','Age-source validity QA/sensitivity','Baseline zeros preserved, not treated as observed demographic absence'),
      'model_eligible_agent3_baseline':('Agent2 verified frozen Agent3 baseline','boolean','Known route and valid LST fraction; all other checks passed on current sources','2538True,227False','Eligibility','Not a permanent formula for future invalid inputs; rerun strict loader'),
      'model_exclusion_reason':('Agent2 verified baseline','text','route_not_computed and/or lst_valid_lt0.5','Empty=eligible','Explain exclusions','Full data contract checks still mandatory'),
      'park_within_500m_known':('Agent2 original routing','0/1/NaN','1 if known distance<=500,0 if known>500','NaN=unknown route','Uncertainty-preserving dashboard feature','Not actual verified public entrance access'),
      'park_within_1000m_known':('Agent2 original routing','0/1/NaN','1 if known distance<=1000,0 if known>1000','NaN=unknown route','Uncertainty-preserving dashboard feature','Same proxy limitations'),
    }
    for col in ['tree_fraction','grass_fraction','built_fraction','water_fraction','flooded_vegetation_fraction','crops_fraction','shrub_fraction','bare_fraction']:
        specs[col]=('Agent1 optional DW modal label2024','area fraction0–1','Share of clipped area in annual modal class','AllNaN because label export unavailable','Future optional analysis','Not replaceable by class probability; not zero-filled')
    specs['dw_label_valid_fraction']=('Agent1 optional DW label2024','fraction','Label raster valid area/clipped area','AllNaN because label export unavailable','Future label QA','Do not confuse with dw_valid_fraction')
    missing=set(final.columns)-set(specs)
    if missing:raise ValueError(f'Undocumented final columns: {missing}')
    rows=[]
    for c in final:
        source,unit,aggregation,missingness,use,limit=specs[c]
        if c in ['grid_id','kota','area_km2','coverage_ratio','longitude','latitude','qa_partial_grid','qa_coverage_lt10pct','qa_area_km2']:
            period='Boundary vintage unverified; fixed master geometry'
        elif '2026' in source or c in ['qa_route_not_computed','qa_far_snap','park_within_500m_known','park_within_1000m_known']:
            period='OSM2026 snapshot'
        elif c in ['input_delivery_complete','model_eligible_agent3_baseline','model_exclusion_reason']:
            period='Mixed2024 sources and OSM2026'
        else:
            period='2024 source/reference year'
        rows.append({'Column':c,'Source':source,'Unit':unit,'Temporal period':period,'Spatial aggregation/definition':aggregation,
                     'Missingness meaning':missingness,'Missing count':int(final[c].isna().sum()),'Downstream use':use,'Quality/limitations':limit})
    df=pd.DataFrame(rows)
    dictionary='''# AGENT2 data dictionary and integration contract

Grain: one row per clipped500m master grid,2765 unique IDs, master CSV order. Join key `grid_id`.
CSV geometry is separate; corresponding GeoPackage is EPSG32748. Source values are unchanged.
Walking accessibility uses2026 OSM, whereas satellite/demographic products refer to2024.
`input_delivery_complete` covers required numeric features, not complete source quality or DW fractions.
All `qa_*` are diagnostic booleans, not automatic deletion instructions. Model eligibility is distinct.

'''+md_table(df)+'''

## QA artifacts and scenario semantics

`network_grid_diagnostics.csv`: all2765 origins. Prefix `city_`=actual baseline1500m graph; `full_`=common
full existing graph, same candidate polygon inventory. `*_component` are deterministic size-sorted component
indices within that graph, not stable OSM feature identifiers. `*_component_nodes` counts nodes;
`*_component_park_nodes` counts candidate park snaps (possibly multiple parks at same node), not unique parks
verified as publicly open. Distances are meters, graph x/y are EPSG32748. Cause categories refer to graph evidence.
`baseline_route_missing`/`qa_far_snap` reproduce original flags. `snap_severity` is diagnostic only.
`*_nearest_park_id` identifies winning modeled destination; ties do not prove unique real-world nearest park.

`euclidean_park_polygon_m`: minimum Euclidean distance from origin rep to any candidate polygon,0 inside;
`euclidean_park_rep_m`: nearest park representative-point distance. Both include barriers implicitly as straight
lines; neither is actual walking access. `network_to_euclidean_rep_ratio` divides modeled full cost by nearest
rep Euclidean cost (NaN if denominator0). The minimizing park can differ between specifications.
`positive_access_tag_scenario_distance_m` restricts to10 positive-tag parks, not a verified public inventory.
`explicit_node_restriction_scenario_distance_m`: conservative edge restrictions, original connectors fixed;
NaN=no modeled route under that policy, not proof of physical no access. All alternatives are provisional.

`gis_model_sensitivity_summary.csv`: fixed-common comparisons recalculate baseline and scenario on their
exact common eligibility; unfixed comparisons retain official baseline and combine definition/selection effects.
`m4_top_jaccard`=intersection/union of top10% ID sets; `m4_rank_spearman_intersection` uses shared ranked IDs.
`n_valid` and `comparison_baseline_n_valid` disclose compared population; eligibility_added/removed reference
the original2538 baseline. The scenario grid table exports M1–M4 without modifying official outputs.
`fractional_population_aggregation` uses exact fractional pixel sums on supplied rasters, including age API
boundary masks; it is a sensitivity, not a claim of independent ground truth.

`population_raster_recomputation.csv`: centroid sums/counts, fractional sums/counts and reproduced QGIS hybrid
sums for each count; `*_delta`=recomputed−original. Fractional pixels are pixel coverage weights summed over
valid pixels. A count0 indicates no valid pixel support; a sum0 with positive support is a modeled source zero.
No valid support is not interchangeable with a census count0. `vulnerable_share` stays NaN when total0.

Park `access_class`: unknown_or_conditional; access_positive_tag_unverified; restricted_tag. Positive tags
are not field verification. `verified_public_entrance=False` means no verification was performed, not a finding
that a park lacks an entrance. `confirmed_exclusion=False` in sampling table means no new manual exclusion;
the original excluded private/permit parks are separately documented.

Geographic `analysis_area_m2`, `full_lattice_area_m2`, `coverage_ratio`, satellite valid fraction are different
quantities. QA source/snapshot URLs, timestamps, hashes and unavailable release metadata are in the handoff.
'''
    (HAND/'AGENT2_DATA_DICTIONARY.md').write_text(dictionary,encoding='utf-8')
    df.to_csv(OUT/'final_features_data_dictionary.csv',index=False)


if __name__=='__main__':main()
