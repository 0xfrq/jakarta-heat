# Quantitative Reproducibility Audit

**Audit date:** 20 November 2026
**Frozen reference:** RC1 `3b8ed05be92c35bbb2b3a617688540ee856b11c8`
**Audit workspace:** `paper/independent_scientific_audit_2026-11-20`
**Status:** most arithmetic verified; one material manuscript table defect;
several provenance-dependent results unresolved.

---

## 1. Method

I did not trust manuscript tables as inputs. I recomputed from the frozen RC1
CSV/GIS artifacts:

- `data/processed/modeling/merged_grid.csv`
- `data/processed/modeling/priority_models.csv`
- `data/processed/modeling/eligibility_by_model.csv`
- `data/processed/modeling/lisa_m4.csv`
- `data/processed/grid_500m_jakarta.gpkg`
- `outputs/remediation/tables/component_contributions.csv`
- `outputs/remediation/tables/rank_change_attribution.csv`
- `outputs/remediation/tables/priority_membership.csv`
- `outputs/remediation/tables/joint_scenario_priority_sets.csv`
- `outputs/remediation/tables/lisa_tail_permutation_sensitivity.csv`
- `outputs/remediation/tables/lisa_tail_permutation_grid.csv`
- `outputs/remediation/tables/robustness_family_summary.csv`

Scripts and machine-readable evidence are in `scripts/` and `evidence/`.

Independent computation was done with Python 3.12.10, pandas 3.1.1, numpy 2.5.5,
geopandas 1.2.0, libpysal 4.15.1, esda 2.10.0 and scipy 1.18.1 (the RC1
integration environment). The independent LISA recomputation used
`libpysal.weights.Queen.from_dataframe` rather than the project's STRtree fast
path, so it is a genuinely different implementation path.

---

## 2. Verified counts and sample

| Quantity | Independent result | Manuscript / RC1 | Verdict |
|---|---:|---:|---|
| Master grid cells | 2,765 | 2,765 | PASS |
| Common comparison cells | 2,536 | 2,536 | PASS |
| M1 eligible | 2,764 | 2,764 | PASS |
| M2 eligible | 2,764 | 2,764 | PASS |
| M3 eligible | 2,758 | 2,758 | PASS |
| M4 eligible | 2,536 | 2,536 | PASS |
| Excluded union | 229 | 229 | PASS |
| Top-decile budget | 254 | 254 | PASS |
| Spatial observations after island removal | 2,535 | 2,535 | PASS |
| Directed Queen edges | 18,368 | 18,368 | PASS |
| Mean Queen neighbours | 7.245759 | 7.245759 | PASS |

The exclusion decomposition also matches: 222 route-only, 4 route + population
+ age, 2 population-only, 1 low-LST; union 229. The two population-only cells are
`JKT_R003_C031` and `JKT_R057_C063`; the island is `JKT_R013_C019`.

---

## 3. Model scores and ranks

### 3.1 Score reproduction

I recomputed M1–M4 from `merged_grid.csv` with the documented p5–p95 min–max
normalisation, park cap 1,000 m and weights.

| Model | Maximum absolute score difference vs saved | Top-set symmetric difference |
|---|---:|---:|
| M1 | 0.0 | 0 |
| M2 | 0.0 | 0 |
| M3 | 0.0 | 0 |
| M4 | 0.0 | 0 |

This verifies the arithmetic of the formulas as implemented. It does **not**
validate the construct, weights or inputs.

### 3.2 Rank tie-break

The project ranks by descending score, then descending **unclipped** min–max
score, then ascending grid ID. This matters because percentile clipping creates
ties: M1 has 127 cells at the maximum, M4 has 2.

Using a naive `rank(method='first')` on the clipped score gives different
rank-shift values (for example, M1–M4 mean absolute shift ≈308.5 instead of
307.4). Under the documented tie-break, the saved ranks are exactly reproduced:

- M1–M4: mean 307.388, median 239, p90 696.5, max 1,714.
- M1–M2: mean 199.567, median 156.
- M2–M3: mean 129.047, median 88.
- M3–M4: mean 266.671, median 248.

The manuscript documents the tie-break; this is a strength. A reader who omits
it will get slightly different numbers.

### 3.3 Pairwise comparison

Independent recomputation from scores and the documented tie-break:

| Pair | Spearman | Kendall | Jaccard 10% | Shared/254 | Mean abs rank shift |
|---|---:|---:|---:|---:|---:|
| M1–M2 | 0.936167 | 0.782120 | 0.567901 | 184 | 199.567 |
| M1–M3 | 0.905442 | 0.736354 | 0.481050 | 165 | 235.532 |
| M1–M4 | 0.846849 | 0.657796 | 0.384196 | 141 | 307.388 |
| M2–M3 | 0.963814 | 0.855851 | 0.687708 | 207 | 129.047 |
| M2–M4 | 0.881550 | 0.700825 | 0.391781 | 143 | 283.483 |
| M3–M4 | 0.897767 | 0.735745 | 0.411111 | 148 | 266.671 |

These match the manuscript’s Table 6 after rounding.

---

## 4. Shapley attribution

Independent recomputation from `rank_change_attribution.csv`:

- Sum of the three Shapley contributions vs `rank_gain`: maximum absolute error
  **2.27 × 10⁻¹³**.
- Absolute shares: **park 85.461251%**, **reweighting 13.249435%**, **age
  1.289314%**.
- Mean absolute per-cell contributions: park 237.466, reweighting 36.815, age
  3.583 rank positions.

This verifies the manuscript’s 85.46/13.25/1.29 values. The decomposition is
descriptive of the model change; it is not a causal effect.

---

## 5. Demographic specification

Independent recomputation against the M4 top decile:

| Scenario | Shared/254 | Jaccard |
|---|---:|---:|
| Total-count swap | 251 | 0.976654 |
| Vulnerable share | 131 | 0.347480 |
| Child share | 158 | 0.451429 |
| Elderly share | 143 | 0.391781 |

Spearman age count vs total population = 0.999479; vulnerable share mean 0.2955,
SD 0.0073, 5th–95th 0.2894–0.3016; vulnerable share vs LST = 0.005726. These
match the manuscript.

---

## 6. Park cutoff and near-park arithmetic

| Quantity | Independent result |
|---|---:|
| M4 top cutoff | 0.8737398492744993 |
| Near-park cells (≤500 m) | 537 |
| Near-park cells in top 254 | 0 |
| Maximum score among near-park cells | 0.8696487759284656 |
| Cutoff minus near-park maximum | 0.004091073 |
| Minimum park distance in top 254 | 638.2027978 m |
| Top cells at 1,000 m cap | 174 / 254 |
| Top population | 1,539,790.68 |
| Common population | 10,519,840.52 |
| Top population share | 14.637% |
| Top area | 63.412 km² |

Example `JKT_R056_C048`: LST 45.58 °C, population 6,971.49, park distance
487.960 m, M4 score 0.869648776, rank 274, 236/254 top cells cooler. All match
the manuscript.

---

## 7. Selection profile

| Group | n | Population | LST mean | NDVI mean | Coverage | Snap |
|---|---:|---:|---:|---:|---:|---:|
| Included | 2,536 | 10,519,840.5 | 41.486 | 0.315 | 0.940 | 49.98 |
| Excluded | 229 | 463,696.6 | 40.283 | 0.365 | 0.821 | 98.81 |

Excluded share: 8.28% of grids, 4.22% of modelled population. City distribution:
East 96, North 77, South 28, West 22, Central 6. These match the manuscript and
the RC1 audit.

---

## 8. LISA

Independent recomputation with `libpysal`/`esda`:

| Model/convention | Significant | HH | LL | HL | LH | ns |
|---|---:|---:|---:|---:|---:|---:|
| M1 directed/999/BH | 818 | 433 | 360 | 12 | 13 | 1,717 |
| M2 directed/999/BH | 837 | 437 | 375 | 16 | 9 | 1,698 |
| M3 directed/999/BH | 782 | 442 | 324 | 11 | 5 | 1,753 |
| M4 directed/999/BH | 663 | 319 | 323 | 11 | 10 | 1,872 |
| M4 two-sided/999/BH | 496 | — | — | — | — | — |
| M4 directed/9,999/BH | 687 | 355 | 309 | 10 | 13 | 1,848 |
| M4 two-sided/9,999/BH | 493 | 252 | 227 | 7 | 7 | 2,042 |
| M4 directed/999/BY | 0 | 0 | 0 | 0 | 0 | 2,535 |
| M4 directed/9,999/BY | 284 | 122 | 157 | 3 | 2 | 2,251 |
| M4 two-sided/9,999/BY | 234 | 109 | 124 | 1 | 0 | 2,301 |

Moran’s I: M1 0.671106279, M2 0.654014824, M3 0.664420702, M4 0.593024954;
expected value −0.000394633; `p_sim` 0.001 at 999 permutations (resolution
limit). The saved M4 LISA p-values match the independent recomputation exactly
(max abs difference 0.0), and the saved FDR labels match exactly.

The **BY/999 = 0** result is a resolution artifact: the minimum attainable
p-value (0.001) is above the BY threshold at that permutation count. It is not
evidence of no clustering. At 9,999 permutations BY yields 284 directed and 234
two-sided significant cells.

---

## 9. Scenario-family sensitivity

Independent recomputation from `joint_scenario_priority_sets.csv`, filtering
`comparison = eligibility_changing_refit_anchors` and comparing each scenario's
top-254 set with the M4 top-254 set:

| Family | Scenarios | Min J | Max J |
|---|---:|---:|---:|
| Aggregation | 1 | 0.881481 | 0.881481 |
| Park threshold | 4 | 0.520958 | 0.682119 |
| Weights | 9 | 0.867647 | 0.953846 |
| QA exclusions | 3 | 0.968750 | 0.996063 |
| Missing park distance | 2 | 0.906475 | 0.906475 |
| Joint factorial | 16 | 0.582555 | 0.727891 |
| Missing support | 1 | 1.000000 | 1.000000 |
| Normalisation | 3 | 0.733788 | 0.814286 |
| Population definition | 2 | 0.347480 | 0.976654 |
| Route policy | 5 | 0.420168 | 1.000000 |
| Thermal support | 2 | 1.000000 | 1.000000 |
| Land cover | 1 | 0.782456 | 0.782456 |

These match Table 10. The table is a family-specific envelope, not an
all-family robustness claim.

---

## 10. Material discrepancy: Table 7 mixes M3 and M4 baselines

This is the most important reproducibility finding of the audit.

### 10.1 What the manuscript says

Table 7 caption:

> “All comparisons use fixed cell identifiers and fixed normalisation anchors.
> The reference is M4. Jaccard is the overlap with the M4 top decile.”

Footnote:

> “‘Retained’ counts cells in both the scenario and M4 top sets.”

The text says:

> “Adding the park term ... yields a top-decile Jaccard of 0.490 ... Reweighting
> alone yields 0.961 ... the age swap alone yields 0.984 ... Adding park plus
> reweighting yields 0.415; age plus park yields 0.499; all three changes yield
> 0.411.”

### 10.2 What the source tables contain

`matched_weight_comparison.csv` compares each coalition to **M3**, not M4:
`compare_rankings(by_id(v, ranks["m3"]), ...)`. `ablation_comparison.csv`
compares construct variants to **M4**.

### 10.3 Exact independent recomputation

| Scenario | M4-relative J | Shared/254 | M3-relative J | Shared/254 |
|---|---:|---:|---:|---:|
| M3 | 0.411111 | 148 | 1.000000 | 254 |
| M4 | 1.000000 | 254 | 0.411111 | 148 |
| Reweighting only | **0.422969** | **151** | 0.961390 | 249 |
| Age swap only | **0.418994** | **150** | 0.984375 | 252 |
| Park addition only | **0.860806** | **235** | 0.489736 | 167 |
| Age + reweighting | **0.422969** | **151** | 0.953846 | 248 |
| Park + reweighting | **0.976654** | **251** | 0.415042 | 149 |
| Age + park | **0.847273** | **233** | 0.498525 | 169 |

### 10.4 Consequence

The manuscript’s Table 7 values for reweighting, age, park addition and their
combinations are **M3-relative**, not M4-relative. The caption and footnote are
false for those rows. The table must be split into:

- **Table 7a — incremental effects relative to M3**: M3 reference 1.000;
  reweighting 0.961/249; age 0.984/252; park 0.490/167; combinations; M4
  0.411/148.
- **Table 7b — construct/ablation comparisons relative to M4**: M4 reference
  1.000; M3 0.411/148; reweighting 0.423/151; age 0.419/150; park 0.861/235;
  combined; no-park 0.423/151; park-only 0.028/14; heat-only 0.384/141;
  equal-weight 0.868/236; total-count 0.977/251; vulnerable-share 0.347/131;
  child-share 0.451/158; elderly 0.392/143; proportional 0.924/244.

Alternatively, keep one table but label every row’s baseline explicitly. The
text must then state which comparison supports the “park dominates” claim. The
claim survives both framings but with different numbers:

- M3-relative: park addition changes the M3 set most (J=0.490 vs 0.961/0.984).
- M4-relative: park addition alone is closest to M4 (J=0.861), while
  reweighting/age alone are far (0.423/0.419).

The hybrid table was not publishable. **Post-audit revision:** the current
manuscript has been corrected by splitting it into Table 7 (incremental,
M3-relative) and Table 8 (construct/ablation, M4-relative). The arithmetic
finding is retained here as the audit record; the representation defect is
resolved in the current manuscript.

---

## 11. RC2 engineering state

RC2 exists on branch `integration/rc2`; current HEAD
`3439f38d38e9b7e844524a59d034bdf8711366d1`, clean. Its receipt reports:

- source `ac656e5b1b123d3bb5c5f618489682109bba2de9`
- artifact `267ebf78efc985926abd2ad64ec4d669138e1a6e`
- implementation SHA-256 `1858264d...`
- 236 tests + 7 subtests, 0 failures, clean checkout
- 63 tables replay, max difference 0.0
- 2,765 master / 2,536 common / 2,535 spatial
- Moran M4 0.593024953816681
- M1/M2/M3/M4 eligibility 2,764/2,764/2,758/2,536
- model definitions byte-identical to RC1; still `PROVISIONAL_UNSIGNED`
- scientific status HOLD

I inspected the RC2 handoff/receipt but did not substitute RC2 for RC1. The RC2
engineering changes are portability/receipt/manifest fixes, not scientific model
changes. The manuscript currently reports the RC1 clean-checkout failure; that
statement is historically true but outdated if RC2 is adopted. This is a
reproducibility-documentation issue, not a numerical error.

---

## 12. Verified versus unresolved

### Verified

- Master/common/eligibility counts.
- M1–M4 scores and ranks (documented tie-break).
- Jaccard/rank-shift table.
- Shapley shares and sum identity.
- Demographic swaps.
- Park cutoff, near-park exclusion, example cell.
- Selection profile.
- Moran/LISA counts under all tested conventions.
- Scenario-family ranges.
- Table 6, 8, 9, 10 values.
- PDF arithmetic and references (61 cited entries; 0 undefined).

### Unresolved / not independently verified

- Original Landsat scene IDs, dates, task IDs, AOI hash, processing date.
- Raw-to-raster reproduction from original GEE scenes.
- Public park access, entrances, legal connector status.
- Historical 2024 OSM network.
- External health outcomes or intervention effectiveness.
- Whether the 2024 thermal composite is seasonally representative.
- Whether the six unsupported demographic cells can be recovered.
- RC2 full numerical identity (I inspected the receipt, not the full pipeline).
- The manuscript’s Table 7 as written (it is internally inconsistent).

---

## 13. Reproducibility verdict

**Arithmetic:** reproducible and independently verified.

**Input provenance:** partially reproducible; Landsat lineage blocked; WorldPop
raw source not independently re-downloaded.

**Code:** RC1 frozen artifact reproducible for tables; RC2 engineering fixes
portability and clean-checkout tests.

**Manuscript:** one material table/label defect prevents a “reproducible
manuscript” verdict until corrected.

**Bottom line:** strong computational reproducibility, conditional input
provenance, and a correctable reporting defect in the central attribution table.
