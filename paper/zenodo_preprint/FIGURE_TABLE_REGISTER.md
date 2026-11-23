# Figure and Table Register

**Manuscript:** From Thermal Hotspots to Spatial Priorities
**Frozen data version:** RC1 `3b8ed05be92c35bbb2b3a617688540ee856b11c8`
**Common sample:** 2,536 cells unless stated otherwise

All figures were generated from RC1 tabular/GIS sources for this manuscript; no
synthetic values were introduced. Tables are booktabs/`tabularx` constructs, not
screenshots. Provenance is repeated in `SOURCE_PROVENANCE.md` and in the
supplement's Table S6.

## Main figures

| Figure | File | Source data | Sample / model | Legend and units | Caption status | Limitations / QA |
|---|---|---|---|---|---|---|
| Fig. 1 | `input/Figures/fig02_environment.pdf` | `merged_grid.csv`, `priority_models.csv`, `grid_500m_jakarta.gpkg` | 2,536 common; M1–M4 eligibility | LST °C; NDVI unitless; grey = excluded | Present | Surface temperature, not air temperature; 5th–95th colour limits; figure generated for this manuscript |
| Fig. 2 | `fig03_population_access.pdf` | same | 2,536 common | log10 population per grid; park distance metres capped 1,000 | Present | Population modelled; park distance candidate proxy; 1,146 cells at cap |
| Fig. 3 | `fig04_priority_maps.pdf` | same | 2,536 common; M1 and M4 | red = top 254; light grey = eligible non-top; dark grey = excluded | Present | Screening map, not intervention map; same extent/classification for both panels |
| Fig. 4 | `fig05_rank_shift.pdf` | `priority_models.csv` | 2,536 common; M1 vs M4 | ranks 1–2,536; signed rank change | Present | Dotted lines at rank 254; median signed −14 vs median absolute 239 explained |
| Fig. 5 | `fig06_attribution_sensitivity.pdf` | `rank_change_attribution.csv`, `robustness_family_summary.csv` | M3→M4; 10% budget | Shapley %; Jaccard 0–1 | Present | Descriptive decomposition; family envelope is incomplete (two families blocked) |
| Fig. 6 | `fig07_lisa.pdf` | `lisa_m4_primary.csv`, `lisa_tail_permutation_sensitivity.csv` | 2,535 non-island; M4 | HH/LL/HL/LH/ns; counts by convention | Present | Adopted two-sided/9,999/BH; BY/999 zero is resolution artifact; not causal |

## Main tables

| Table | File | Source | Content | Units / notes | Status |
|---|---|---|---|---|---|
| 1 | `Tables/table2_literature.tex` | Literature matrix | Selected prior work and positioning | Citations, not new numbers | Verified metadata; not systematic review |
| 2 | `Tables/table10_park.tex` | `park_access_evidence.csv` | Candidate park evidence states | Counts and shares; 0 verified access/entrance | Verified counts |
| 3 | `Tables/table1_sources.tex` | Data documentation | Sources, periods, processing, limitations | Metadata table | Mixed-period disclosure |
| 4 | `Tables/table4_eligibility.tex` | `eligibility_by_model.csv` | Master/common/excluded counts | Cells | Verified |
| 5 | `Tables/table3_models.tex` | `model_specification.json` | M1–M4 formulas and weights | Provisional weights | Exact formula reproduction |
| 6 | `Tables/table5_comparison.tex` | `model_comparison.csv`, `jaccard_matrix.csv`, `rank_movement.csv` | Pairwise Spearman/Kendall/Jaccard/rank shift | 2,536 cells; 5/10/20% budgets | Verified |
| 7 | `Tables/table6a_attribution_m3.tex` | `matched_weight_comparison.csv` | Incremental effects relative to M3 | Jaccard and shared/254; M3 baseline | Verified; corrected/split |
| 8 | `Tables/table6b_attribution_m4.tex` | `ablation_comparison.csv`, `matched_weight_comparison.csv` | Construct/ablation comparisons relative to M4 | Jaccard and shared/254; M4 baseline | Verified; corrected/split |
| 9 | `Tables/table9_selection.tex` | `eligibility_selection_profile.csv` | Included vs excluded profile | Means; population sum | Verified descriptive profile |
| 10 | `Tables/table8_lisa.tex` | `lisa_tail_permutation_sensitivity.csv`, `lisa_m4_primary.csv` | LISA convention sensitivity | 2,535 cells | Verified; primary two-sided/9,999/BH; convention range |
| 11 | `Tables/table7_sensitivity.tex` | `robustness_family_summary.csv` | Scenario-family min/max Jaccard | 10% budget | Verified; incomplete envelope |

## Supplementary figures

| Figure | File | Source | Purpose | Limitations |
|---|---|---|---|---|
| S1 | `figS2_exclusions.pdf` | `eligibility_by_model.csv`, grid | Map excluded cells by primary reason | Reasons overlap; primary order is a display choice |
| S2 | `figS1_score_distributions.pdf` | `priority_models.csv` | Score distributions M1–M4 | Descriptive; not model-accuracy evidence |
| S3 | `figS3_park_inventory.pdf` | `parks_jakarta.gpkg`, `park_access_evidence.csv`, grid | Candidate parks by evidence state; route-missing grid | Candidate proxy; points are representative points, not entrances |

## Supplementary tables

| Table | File / location | Content | Source |
|---|---|---|---|
| S1 | `input/Supplementary.tex` | Data quality and missingness | `data_quality.csv`, `demographic_support.csv` |
| S2 | `input/Supplementary.tex` | Scenario-family sensitivity at 5/10/20% | `robustness_family_summary.csv` |
| S3 | `input/Supplementary.tex` | City composition of top deciles | `kota_summary.csv` |
| S4 | `input/Supplementary.tex` | LISA cluster counts M1–M4 | `lisa_cluster_counts.csv` |
| S5 | `input/Supplementary.tex` | M4 LISA convention sensitivity | `lisa_tail_permutation_sensitivity.csv` |
| S6 | `input/Supplementary.tex` | All 49 executed scenario comparisons | `Supplementary_Tables/full_scenario_results.csv` |
| S7 | `input/Supplementary.tex` | Six demographic no-support cells | `Supplementary_Tables/demographic_no_support.csv` |
| S8 | `input/Supplementary.tex` | Master-to-common eligibility reconciliation | `Supplementary_Tables/eligibility_reconciliation.csv` |
| S9 | `input/Supplementary.tex` | Figure/table provenance | This register and RC1 handoff |

## Figure QA performed

- Rendered all main figures at 300–400 dpi in the PDF and checked legends,
  colour bars, units, labels and panel titles.
- Checked that excluded cells are shown in every priority/selection map.
- Checked that no map uses a dashboard screenshot or an Indonesian-language
  caption.
- Checked that the park-distance map does not label capped cells as zero; the
  cap is stated in the caption.
- Checked that the LISA map and bar chart name the convention and warn against
  causal interpretation.
- Checked that the supplement's S1–S3 figures appear in the intended order.

## Table QA performed

- All tables use `booktabs` rules and `tabularx`/`threeparttable` where needed.
- Tables 7–8 (attribution split) and Table 11 (scenario family) were checked for
  float/caption collisions after a rendered-PDF review; `[H]` placement and
  `\belowcaptionskip` were adjusted.
- Table 6 (comparison) was checked after the same review; `[H]` placement was
  used to avoid a caption collision with Fig. 4.
- No table is a screenshot; all values are typeset from RC1 tables.
- Values in Tables 4–11 were cross-checked against the independent audit and/or
  RC1 CSV outputs.

## Missing or not included

- No figure shows a verified park entrance or public-access route, because none
  is verified.
- No figure shows 2024 OSM access, because the OSM snapshot is 2026.
- No figure shows health outcomes, because no health outcome data are used.
- No figure shows RC2 scenarios, because RC2 is not the frozen reference.
