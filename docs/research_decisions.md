# Scientific decisions proposed after independent audit (20 November 2026)

RC1 engineering update: the authorized integration rebuilds standard and expanded
outputs from canonical A1/A2 inputs. Historical audited features/priorities remain
under `data/processed/remediation_inputs/audited_*` and Agent 2's baseline evidence.
The paragraphs describing the original candidate's 19-cell auditor support and
missing route versions are historical: RC1 uses buffered source support (six
unsupported age cells, 13 recovered) and executes all five Agent 2 route versions.
Fractional scenarios use Agent 2's corrected buffered surfaces. The 16-scenario
factorial covers construct/cap/normalization/aggregation; route policies are a
separate family, so this is not an all-family joint robustness claim. Every
scientific approval below remains pending; integration does not supply sign-off.

**All choices below are UNSIGNED proposals or exploratory scenarios.** This file records the exact decisions for coordinator review; it is not retrospective preregistration. Original audited M1–M4 outputs remain in `data/processed/modeling` and `outputs/tables`. Candidate results are in `data/processed/modeling_remediation` and `outputs/remediation`. No official model is silently replaced.

## temporal_scope — TM-01 (coordinator approval pending)

Recommend a mixed-reference-period, exploratory screening study of five mainland Jakarta cities: 2024 surface-temperature/vegetation composites and modeled demographic estimates paired with the OSM candidate parks/network extracted 19 November 2026. This avoids an unsupported common-year interpretation. Withdraw claims of actual public access in 2024, temporal stability/change, contemporaneous effects, current 2026 heat exposure, and causal health/policy benefits. Actual 2024 accessibility requires comparable historical parks AND network plus evidence about physical usability; a historical OSM record alone establishes mapping history. No temporal materiality estimate is available. TM-02 is conditional on the coordinator retaining historical claims; it is not marked PASS by an absent pilot.

## constructs_weights — MD-01 (coordinator approval pending)

Decision: count-oriented screening, composition-oriented screening, or both? Recommend reporting two dimensions: the modeled number of age-sensitive residents and their share of supported total population, with count M4 retained as a **provisional exposure-oriented screening index** and shares as a distinct question. Neither additive log-count score measures individual exposure, dose, mortality, or policy superiority. Counts have units persons/grid before transformation; composition is a dimensionless share with a supported, strictly positive total-population denominator. Child/elderly shares are also evaluated separately. A supported population zero may have count zero, but its composition is undefined. NoData cannot be assigned demographic zero.

The inherited weights are M1 L=1; M2 .6L+.4V; M3 .4L+.3V+.3P; M4 .3L+.2V+.25A+.25D. They remain provisional rather than empirically optimal. P and A use log1p to compress count magnitude; this changes the objective relative to linear total burden. L/V/P/A use 5th–95th percentile clipped min-max within a declared universe. Fixed-term ablations keep the same IDs and anchors. All-grid/model-specific comparisons intentionally use different universes and report them. Exact anchors are exported. Rank ties use unclipped min-max score then grid ID. Top budgets are ceil(.05n), ceil(.10n), ceil(.20n); these are planning budgets, not health thresholds.

D=min(modeled candidate-park network distance,1000)/1000. The cap is an inherited planning-scale saturation assumption, not a measured cooling distance or safe walking threshold. Alternatives use caps 750/1500 m and binary 500/1000 m. Broad non-explicitly-restricted OSM candidate polygons remain an uncertain proxy pending AC-01/02; positive-tag-only deletion is an extreme destination-coverage stress, never ground truth.

An additional exploratory burden surface uses B=L (relative dimensionless surface burden, fixed p05/p95 anchors), population×B and age_count×B. Its units are modeled persons times relative surface-burden units, **not person-degrees, a health dose, or observed people harmed**. It has no invented health threshold. `count_composition_burden.csv` evaluates this objective without replacing M3/M4.

Evidence: `ablation_comparison.csv`, `component_contributions.csv`, `normalization_anchors.csv`, `rank_change_attribution.csv`, and `count_composition_burden.csv` in candidate tables. Exact M3→M4 score change is −.1L−.1V−.3P+.25A+.25D. Three factors partition it into reweighting (−.1L−.1V−.05P), age swap .25(A−P), and park addition .25D. All six insertion orders inform exact Shapley rank attribution; min/max marginals show order dependence. Arithmetic allocation does not establish causation. A near-zero age-count increment is an acceptable result.

## demographic_missingness — DM-01/DM-02 (canonical source version pending)

Recommendation: null unsupported analytical total/age counts, preserve original exports under `raw_*`, retain all master IDs, and propagate support into per-model eligibility. Do not impute mean age shares. The current candidate uses a versioned copy of auditor pixel-mask evidence: 19 age-no-support and six total-no-support cells. It does not claim to recover source pixels or establish national WorldPop product failure. Agent 2 must supply corrected compatible surfaces/support or document unresolved gaps. Count eligibility needs supported source values; composition additionally needs positive total population. Comparison membership is one common M1–M4 set, while M1–M3 full-area maps have separate denominators.

## thermal_QA — RS-02 (primary threshold approval pending)

`JKT_R037_C062` is delivered: LST 42.234°C, NDVI .2961. Valid LST area 6724.1312 / clipped cell 24223.1114 m² ≈ .277592. Clipped/nominal area ≈ .096892 is a different denominator. The inherited .50 support threshold is a provisional modeling QA decision, never a delivery failure. Compare .50, .25/inclusion-as-flagged, and .50 plus Agent 1 QA status, holding non-RS eligibility and baseline anchors fixed. Flagged inclusion is acceptable as a sensitivity; no observed value or flag is cleared. Recommend retaining .50 for continuity until Agent 1's temporal/uncertainty support and coordinator rationale are available, with explicit .25 sensitivity. `rs_eligibility_sensitivity.csv` and `rs_target_support.json` quantify the effects; no threshold is chosen to improve the priority map.

## scenario_envelope — MD-03 (approval pending)

`scenario_registry.csv` identifies executed, blocked, and conditional families. Executed one-at-a-time alternatives cover weights, normalization, missing-route stress, count/share/density, probability-based land cover, partial cells/snaps, thermal support and fractional allocation. The bounded joint factorial has 16 scenarios: age/total count × 750/1500 m cap × clipped/rank normalization × legacy/fractional aggregation, with supported demographics in every scenario. This envelope is provisional and deliberately omits no unavailable family silently: destination/entry/barrier alternatives remain BLOCKED pending per-grid Agent 2 route versions; seasonal composites remain BLOCKED pending RS-01. Temporal alternatives are conditional on TM-01. No all-family robustness or confidence probability follows from executed-family frequencies. Registry membership and fixed/intersection versus changing-universe comparisons are exported.

## spatial_inference — ST-01 (substantive alternative/family approval pending)

Record the existing directed local convention explicitly; evaluate two-sided local tests and 9999 permutations, plus BH and conservative BY corrections. Proposed family is each preselected model-map separately, all eligible non-island grids. This choice is not approval for arbitrary repeated map selection. See `spatial_inference_spec.md` and per-grid sensitivity. Cluster labels are descriptive only.

## claim_scope — NV-01/NV-02/QA-01 (coordinator and independent re-audit pending)

Recommended contribution: Jakarta-specific attribution and uncertainty propagation in exploratory screening decisions, conditional on source corrections and accessible predecessor comparison. No novelty is claimed for combining heat, age and access, for changed rankings, a dashboard, or significant Moran I. The auditor's literature review is the current evidence; Agent 3 has not claimed a new systematic review. Heat-only and equal-weight benchmarks are transparent internal rules, not independent validation. Independent park/operator/entrance evidence must be integrated from AC-01/02. External health/policy outcomes are unavailable; no superiority claim is made. Scientific sign-off, consolidated candidate and independent acceptance remain open.
