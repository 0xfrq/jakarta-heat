# AGENT2 data dictionary and integration contract

Grain: one row per clipped500m master grid,2765 unique IDs, master CSV order. Join key `grid_id`.
CSV geometry is separate; corresponding GeoPackage is EPSG32748. Source values are unchanged.
Walking accessibility uses2026 OSM, whereas satellite/demographic products refer to2024.
`input_delivery_complete` covers required numeric features, not complete source quality or DW fractions.
All `qa_*` are diagnostic booleans, not automatic deletion instructions. Model eligibility is distinct.

| Column | Source | Unit | Temporal period | Spatial aggregation/definition | Missingness meaning | Missing count | Downstream use | Quality/limitations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| grid_id | Master | identifier | Boundary vintage unverified; fixed master geometry | 500m projected lattice cell clipped to boundary | Never missing; unique key | 0 | All joins | Stable grid version required |
| kota | Master | city label | Boundary vintage unverified; fixed master geometry | Largest overlap administrative owner | Never missing | 0 | Summaries | May differ from representative-point routing partition |
| area_km2 | Master geometry | km² | Boundary vintage unverified; fixed master geometry | Clipped analysis polygon area | Never missing | 0 | Area/edge QA | Not full250000m² footprint |
| coverage_ratio | Master geometry | fraction | Boundary vintage unverified; fixed master geometry | Analysis area /250000m² | Never missing | 0 | Edge QA | Not satellite valid fraction or measured land cover |
| longitude | Master geometry | degrees east | Boundary vintage unverified; fixed master geometry | Clipped representative point EPSG4326 | Never missing | 0 | Display | Not population-weighted location |
| latitude | Master geometry | degrees north | Boundary vintage unverified; fixed master geometry | Clipped representative point EPSG4326 | Never missing | 0 | Display | Not population-weighted location |
| population | WorldPop total2024 R2025A v1 | modeled persons | 2024 source/reference year | QGIS hybrid pixel sum | 0 is modeled count; no missing | 0 | Exposure | Model estimates; not census counts; hybrid allocation |
| pop_child | WorldPop API agesex2024 R2025A | modeled persons0–14 | 2024 source/reference year | Both sexes; QGIS hybrid sum | 0 can be empty raster support; inspect QA | 0 | Age count component | API source mask differs at boundary; not field age census |
| pop_elderly | WorldPop API agesex2024 R2025A | modeled persons65+ | 2024 source/reference year | Includes90+; QGIS hybrid sum | 0 can be empty raster support; inspect QA | 0 | Age count component | Same mask limitation as children |
| park_distance_m | Person2 OSM2026 | meters | OSM2026 snapshot | Origin connector+network shortest path+park rep connector | NaN=routing not computed; never zero-imputed | 226 | M4 baseline | Approximate points, no verified entrances/public access |
| grid_snap_m | Person2 OSM2026 | meters | OSM2026 snapshot | Euclidean origin rep to nearest graph node | No missing in baseline | 0 | Snap QA | Straight connector may cross barriers; simplified nodes |
| park_reachable | Person2 OSM2026 | 0/1 | OSM2026 snapshot | 1 iff modeled distance computed | 0=unknown/uncomputed route, not proven no real-world access | 0 | Legacy contract | Name can mislead; use qa_route_not_computed |
| park_access_500m | Person2 OSM2026 | 0/1 | OSM2026 snapshot | Legacy1 if computed distance<=500m | 0 includes both known>500 and unknown distance | 0 | Legacy dashboard | Use park_within_500m_known to preserve uncertainty |
| park_access_1000m | Person2 OSM2026 | 0/1 | OSM2026 snapshot | Legacy1 if computed distance<=1000m | 0 includes unknown distance | 0 | Legacy dashboard | Use park_within_1000m_known |
| lst_mean_c | Agent1 Landsat9 C2 L2,2024 | °C | 2024 source/reference year | Exact coverage-weighted cell mean of pixel temporal median | No missing delivered | 0 | M1–M4 via lst_c alias | Surface clear-sky sampling; not air temperature |
| ndvi_mean | Agent1 Landsat9,2024 | index −1..1 | 2024 source/reference year | Exact cell mean of pixel temporal median NDVI | No missing | 0 | Vegetation | Spectral proxy, not usable park supply |
| tree_fraction | Agent1 optional DW modal label2024 | area fraction0–1 | 2024 source/reference year | Share of clipped area in annual modal class | AllNaN because label export unavailable | 2765 | Future optional analysis | Not replaceable by class probability; not zero-filled |
| grass_fraction | Agent1 optional DW modal label2024 | area fraction0–1 | 2024 source/reference year | Share of clipped area in annual modal class | AllNaN because label export unavailable | 2765 | Future optional analysis | Not replaceable by class probability; not zero-filled |
| built_fraction | Agent1 optional DW modal label2024 | area fraction0–1 | 2024 source/reference year | Share of clipped area in annual modal class | AllNaN because label export unavailable | 2765 | Future optional analysis | Not replaceable by class probability; not zero-filled |
| lst_valid_fraction | Agent1 Landsat9,2024 | fraction | 2024 source/reference year | Area with valid LST /clipped polygon area | No missing;0.277592 minimum | 0 | Agent3 lst_valid_frac alias and threshold | Not fraction of full square or fraction of dates |
| lst_observation_count | Agent1 Landsat9,2024 | observations per pixel | 2024 source/reference year | Coverage-weighted mean of valid pixel counts | No missing | 0 | Agent3 lst_obs alias | Unequal seasonal/scene support |
| lst_std_c | Agent1 Landsat9,2024 | °C | 2024 source/reference year | Spatial SD of pixel median LST | No missing | 0 | Within-cell QA | Not uncertainty of annual median |
| lst_min_c | Agent1 Landsat9,2024 | °C | 2024 source/reference year | Min touching valid pixel median LST | No missing | 0 | QA | Partial-pixel inclusion; not daily minimum |
| lst_max_c | Agent1 Landsat9,2024 | °C | 2024 source/reference year | Max touching valid pixel median LST | No missing | 0 | QA | Not annual daily maximum |
| lst_unc_mean_k | Agent1 Landsat9 ST_QA,2024 | K | 2024 source/reference year | Cell mean of per-pixel median scene uncertainty | No missing | 0 | Agent3 lst_unc_k alias | Not uncertainty of final median/composite |
| lst_observation_min | Agent1 Landsat9,2024 | observations | 2024 source/reference year | Minimum clear LST count in cell | No missing | 0 | QA | Not a per-grid scene count |
| ndvi_std | Agent1 Landsat9,2024 | index | 2024 source/reference year | Spatial SD of median NDVI | No missing | 0 | QA | Not temporal variability |
| ndvi_valid_fraction | Agent1 Landsat9,2024 | fraction | 2024 source/reference year | Valid NDVI pixel area/clipped area | No missing | 0 | Coverage QA | Different from LST valid fraction |
| landsat_footprint_fraction | Agent1 Landsat9 export,2024 | fraction | 2024 source/reference year | Export AOI raster support/clipped area | No missing | 0 | AOI alignment QA | Does not prove remote GEE asset byte equality |
| tree_prob_mean | Agent1 Dynamic WorldV1,2024 | probability0–1 | 2024 source/reference year | Cell mean of temporal median per-image tree probability | One sliver cell NaN | 1 | Sensitivity; Agent3 trees_prob alias | Not tree area fraction |
| built_prob_mean | Agent1 Dynamic WorldV1,2024 | probability0–1 | 2024 source/reference year | Cell mean of temporal median per-image built probability | One sliver cell NaN | 1 | Sensitivity; Agent3 built_prob alias | Not built area fraction |
| dw_valid_fraction | Agent1 Dynamic WorldV1,2024 | fraction | 2024 source/reference year | Valid probability raster area/clipped area | Can0 at tiny sliver | 0 | Coverage QA | Probability raster support, not class-label fractions |
| water_fraction | Agent1 optional DW modal label2024 | area fraction0–1 | 2024 source/reference year | Share of clipped area in annual modal class | AllNaN because label export unavailable | 2765 | Future optional analysis | Not replaceable by class probability; not zero-filled |
| flooded_vegetation_fraction | Agent1 optional DW modal label2024 | area fraction0–1 | 2024 source/reference year | Share of clipped area in annual modal class | AllNaN because label export unavailable | 2765 | Future optional analysis | Not replaceable by class probability; not zero-filled |
| crops_fraction | Agent1 optional DW modal label2024 | area fraction0–1 | 2024 source/reference year | Share of clipped area in annual modal class | AllNaN because label export unavailable | 2765 | Future optional analysis | Not replaceable by class probability; not zero-filled |
| shrub_fraction | Agent1 optional DW modal label2024 | area fraction0–1 | 2024 source/reference year | Share of clipped area in annual modal class | AllNaN because label export unavailable | 2765 | Future optional analysis | Not replaceable by class probability; not zero-filled |
| bare_fraction | Agent1 optional DW modal label2024 | area fraction0–1 | 2024 source/reference year | Share of clipped area in annual modal class | AllNaN because label export unavailable | 2765 | Future optional analysis | Not replaceable by class probability; not zero-filled |
| dw_label_valid_fraction | Agent1 optional DW label2024 | fraction | 2024 source/reference year | Label raster valid area/clipped area | AllNaN because label export unavailable | 2765 | Future label QA | Do not confuse with dw_valid_fraction |
| qa_area_km2 | Agent1 master geometry | km² | Boundary vintage unverified; fixed master geometry | Clipped analysis polygon area rounded in CSV | No missing | 0 | Alignment QA | Alias by meaning of area_km2, different rounding |
| rs_qa_flags | Agent1 QA | semicolon-separated text | 2024 source/reference year | partial_lst,edge_cell,high_unc,low_obs,no_lst,footprint_gap | Empty=no reported flags | 2655 | Source QA | Not all flags excluded by Agent3 baseline |
| rs_qa_ok | Agent1 QA | boolean | 2024 source/reference year | False if partial/no LST,low observations,high uncertainty | No missing | 0 | Agent3 sensitivity | 13 false; baseline only excludes low LST fraction1 |
| lst_c | Agent1 alias | °C | 2024 source/reference year | Identical to lst_mean_c | No missing | 0 | Agent3 required | Same LST limitations |
| ndvi | Agent1 alias | index −1..1 | 2024 source/reference year | Identical to ndvi_mean | No missing | 0 | Agent3 required | Same NDVI limitations |
| pop_vulnerable | Agent2 original age counts | modeled persons | 2024 source/reference year | pop_child+pop_elderly | No missing; source-mask zeros retained | 0 | Alternative feature/compatibility | Strongly correlated with total population |
| vulnerable_share | Agent2 original demographic counts | fraction | 2024 source/reference year | pop_vulnerable/population when population>0 | NaN for6 zero-pop cells;19 source-no-support flags | 6 | Age-composition alternative | Agent3 vuln_share convention sets zero-pop0; original formula unchanged |
| input_delivery_complete | Agent2 source contract | boolean | Mixed2024 sources and OSM2026 | LST,NDVI,total,child,elderly all delivered numerically | AllTrue; route missingness handled separately | 0 | Delivery status | Does not imply full GIS validity or complete DW class fractions |
| qa_route_not_computed | Agent2 original routes | boolean | OSM2026 snapshot | park_distance_m is NaN | True=unknown routing | 0 | Missingness QA | Not confirmed lack of access |
| qa_far_snap | Agent2 original snaps | boolean | OSM2026 snapshot | grid_snap_m>250m | False includes known<=250m | 0 | Snap QA | Diagnostic threshold, no automatic exclusion |
| qa_partial_grid | Agent2 master geometry | boolean | Boundary vintage unverified; fixed master geometry | coverage_ratio<1−1e−8 | No missing | 0 | Area QA | Includes any clipped cell; not raster coverage |
| qa_coverage_lt10pct | Agent2 master geometry | boolean | Boundary vintage unverified; fixed master geometry | coverage_ratio<0.1 | No missing | 0 | Tiny-cell QA | Diagnostic threshold |
| qa_lst_low_valid | Agent2/Agent3 QA rule | boolean | 2024 source/reference year | lst_valid_fraction<0.5 | No missing | 0 | Baseline model eligibility | Threshold provisional; not delivery missingness |
| qa_age_zero_pop_positive | Agent2 demographic QA | boolean | 2024 source/reference year | population>0 and both age counts0 | No missing | 0 | Review source support | 14 cases,13 have absent support |
| qa_age_source_no_support | Agent2 raw age raster counts | boolean | 2024 source/reference year | No valid fractional child or elderly pixel intersects grid | No missing;19True | 0 | Age-source validity QA/sensitivity | Baseline zeros preserved, not treated as observed demographic absence |
| model_eligible_agent3_baseline | Agent2 verified frozen Agent3 baseline | boolean | Mixed2024 sources and OSM2026 | Known route and valid LST fraction; all other checks passed on current sources | 2538True,227False | 0 | Eligibility | Not a permanent formula for future invalid inputs; rerun strict loader |
| model_exclusion_reason | Agent2 verified baseline | text | Mixed2024 sources and OSM2026 | route_not_computed and/or lst_valid_lt0.5 | Empty=eligible | 2538 | Explain exclusions | Full data contract checks still mandatory |
| park_within_500m_known | Agent2 original routing | 0/1/NaN | OSM2026 snapshot | 1 if known distance<=500,0 if known>500 | NaN=unknown route | 226 | Uncertainty-preserving dashboard feature | Not actual verified public entrance access |
| park_within_1000m_known | Agent2 original routing | 0/1/NaN | OSM2026 snapshot | 1 if known distance<=1000,0 if known>1000 | NaN=unknown route | 226 | Uncertainty-preserving dashboard feature | Same proxy limitations |


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

## Remediation outputs (DM-01/AC-01/AC-02/BG-01, versioned 20 November 2026)

Legacy files above are preserved unchanged; corrected values live in separate files.
Hashes of every canonical path: `docs/integration_manifest.json`; input hashes:
`docs/agent2_frozen_inputs.json` (v2).

`data/processed/demographic_support.csv` (2765 rows, one per `grid_id`). For each
`<col>` in `population`, `pop_child`, `pop_elderly`: `<col>_support_pixels` = valid
source pixels intersecting the polygon (0 ⇒ no source support);
`<col>_overlapping_pixels` = all intersecting pixels; `<col>_support_fractional_pixels`
= sum of area weights of valid pixels; `<col>_support_area_m2` = projected area of
valid-pixel support within the UTM polygon (clipped to polygon area; GEOS rounding
only); `<col>_support_area_fraction` = that area / polygon area ∈ [0,1];
`<col>_center_pixels` = valid pixels whose centre lies inside (QGIS hybrid rule);
`<col>_support_state` ∈ {`no_source_support`, `valid_estimated_zero`,
`valid_uncertain_estimate`}; `<col>_export_state` ∈ {`processing_empty_sum_zero`,
`supported_source_export`}; `<col>_source_sha256` = raster hash.
`support_version` (= `demographic_support_version`): `agent2-DM-01-v1-buffered-age`
(canonical) or `agent2-DM-01-v1-original-masks` (QA copy under
`outputs/qa/remediation_agent2/original_masks/`). `qa_population_source_no_support`
(bool) = total support pixels 0; `qa_age_source_no_support` (bool) = child or
elderly support pixels 0. These three fields satisfy Agent 3's DM-02 contract.

`data/processed/demographic_features_corrected.csv`: analytical `population`,
`pop_child`, `pop_elderly` (NaN only when no source support; never invented),
`<col>_raw` = legacy export value (including the former empty-sum zeros),
`pop_vulnerable`, `vulnerable_share` (NaN when total is NaN or 0),
`aggregation_method` (`hybrid`), `support_version`.

`data/processed/spatial_features_corrected.csv` and
`final_model_features_corrected.csv/.gpkg` (layer `corrected_source_features`):
legacy columns with corrected demographics plus all support fields,
`qa_total_source_no_support`, `demographic_analytical_complete`,
`model_eligible_corrected_common_proposal` (2536 TRUE; proposal only) and
`model_exclusion_reason_corrected` (semicolon list: `route_not_computed`,
`lst_valid_lt0.5`, `total_no_source_support`, `age_no_source_support`).

`data/processed/agent2_route_scenarios.csv` (long; 2765 rows × scenario):
`scenario_id` ∈ {`audited_baseline`, `full_jakarta_extent`,
`positive_tags_destination_coverage_stress`, `explicit_nodes_conservative`,
`explicit_nodes_and_connectors_conservative`}; `park_distance_m` (m, NaN = no route
under that scenario — unknown, not zero); `metric_label`
(`observed_shortest_path_2026_osm_proxy` / `no_route_under_scenario_unknown_not_zero`);
`stress_assumption`; `network_extent`; `destination_policy`; `permission_policy`;
`connector_policy`; `public_access_verified` (always False); `source_table`,
`source_sha256` (provenance). Scenario metadata: `docs/agent2_scenario_registry.csv`;
reference periods: `docs/agent2_variable_reference_periods.csv`.

`data/processed/park_access_evidence.csv`: one row per candidate park (1015);
`access_evidence_state` ∈ {`unknown`, `conditional_unverified`,
`positive_osm_tag_unverified`, `excluded_restricted`}; `public_access_verified`,
`entrance_verified`, `exact_osm_polygon_identity_verified` all False;
`raw_tags_json` = full archived OSM tags; `evidence_*` = context URL, publication
date (blank unless verified), check time and limited scope.
`data/processed/validated_park_entrances.gpkg` is intentionally empty (typed schema).
`data/processed/walking_permission_manifest.json`: AC-02 policy, precedence, counts.
