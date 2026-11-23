# Final Numerical Consistency Check

**Date:** 21 November 2026
**Scope:** publication candidate (24 pp), internal review PDF (24 pp),
supplementary PDF (8 pp).
**Frozen empirical basis:** RC1 commit
`3b8ed05be92c35bbb2b3a617688540ee856b11c8`.
**Engineering evidence:** RC2 source/artifact receipts; empirical results remain
RC1.

## 1. Sample and eligibility

| Quantity | Value | Source / check |
|---|---:|---|
| Master grid cells | 2,765 | `grid_master.csv`; unique IDs |
| Common comparison cells | 2,536 | `priority_models.csv`; `valid=TRUE` |
| M1 eligible | 2,764 | `eligibility_by_model.csv` |
| M2 eligible | 2,764 | same |
| M3 eligible | 2,758 | same |
| M4 eligible | 2,536 | same |
| Excluded from common comparison | 229 | union of documented reasons |
| Spatial observations after island | 2,535 | Queen graph; `JKT_R013_C019` removed |
| Directed Queen edges | 18,368 | independent graph rebuild |
| Mean Queen neighbours | 7.245759 | independent graph rebuild |

Exclusion decomposition: 222 route-only, 4 route + population + age, 2
population-only, 1 low-LST. The two population-only cells are
`JKT_R003_C031` and `JKT_R057_C063`.

## 2. Model scores and ranks

Independent recomputation from `merged_grid.csv` using the documented p5–p95
normalisation and model weights:

| Model | Max absolute score difference | Rank mismatches | Top-set symmetric difference |
|---|---:|---:|---:|
| M1 | 0.0 | 0 | 0 |
| M2 | 0.0 | 0 | 0 |
| M3 | 0.0 | 0 | 0 |
| M4 | 0.0 | 0 | 0 |

Ranks use descending clipped score, descending **unclipped** score and ascending
grid ID. The unclipped-score tie-break is necessary; a naive rank of the clipped
score gives slightly different displacement values (e.g. M1–M4 mean ≈308.5
instead of 307.4).

## 3. Jaccard and retention

M1 and M4 share **141** of **254** top-decile cells:

- Retention = 141/254 = **55.5%**.
- Union = 254 + 254 − 141 = **367**.
- Jaccard = 141/367 = **0.384196**.
- M1-only = **113**; M4-only = **113**.

This distinction is stated in the Abstract, Results, Discussion, Conclusion and
Table 6 note. Jaccard 0.384 is not the percentage of M1 members retained.

Pairwise 10% Jaccard:

| Pair | Jaccard | Shared/254 | Retention |
|---|---:|---:|---:|
| M1–M2 | 0.567901 | 184 | 72.4% |
| M1–M3 | 0.481050 | 165 | 65.0% |
| M1–M4 | 0.384196 | 141 | 55.5% |
| M2–M3 | 0.687708 | 207 | 81.5% |
| M2–M4 | 0.391781 | 143 | 56.3% |
| M3–M4 | 0.411111 | 148 | 58.3% |

Rank displacement: M1–M4 mean absolute **307.388**, median **239**, p90
**696.5**, maximum **1,714**.

## 4. Attribution

Exact three-factor Shapley decomposition of absolute M3-to-M4 rank movement:

- Park addition: **85.461%**
- Reweighting: **13.249%**
- Age substitution: **1.289%**
- Sum of Shapley contributions vs rank gain: maximum absolute error
  **2.27 × 10⁻¹³**.

Table 7 is **M3-relative** incremental attribution:

| Scenario | Jaccard vs M3 | Shared/254 |
|---|---:|---:|
| M3 reference | 1.000 | 254 |
| Reweighting | 0.961 | 249 |
| Age swap | 0.984 | 252 |
| Park addition | 0.490 | 167 |
| Age + reweighting | 0.954 | 248 |
| Park + reweighting | 0.415 | 149 |
| Age + park | 0.499 | 169 |
| M4 (all changes) | 0.411 | 148 |

Table 8 is **M4-relative** construct/ablation comparison:

| Scenario | Jaccard vs M4 | Shared/254 |
|---|---:|---:|
| M4 reference | 1.000 | 254 |
| M3 | 0.411 | 148 |
| Reweighting | 0.423 | 151 |
| Age swap | 0.419 | 150 |
| Park addition | 0.861 | 235 |
| Age + reweighting | 0.423 | 151 |
| Park + reweighting | 0.977 | 251 |
| Age + park | 0.847 | 233 |
| No park | 0.423 | 151 |
| Park only | 0.028 | 14 |
| Heat only | 0.384 | 141 |
| Equal weight | 0.868 | 236 |
| Total-count swap | 0.977 | 251 |
| Vulnerable share | 0.347 | 131 |
| Child share | 0.451 | 158 |
| Elderly share | 0.392 | 143 |
| Proportional M3 + park | 0.924 | 244 |

The two tables are not interchangeable; the captions and text state their
baselines.

## 5. Demographic specification

- Age count vs total population Spearman: **0.999479**.
- Total-count swap: Jaccard **0.976654**, 251/254 shared.
- Vulnerable-share swap: Jaccard **0.347480**, 131/254.
- Child-share: **0.451429**, 158/254.
- Elderly-share: **0.391781**, 143/254.
- Vulnerable share: mean **0.2955**, SD **0.0073**, 5th–95th
  **0.2894–0.3016**; correlation with LST **0.005726**.

## 6. Park cutoff and near-park arithmetic

| Quantity | Value |
|---|---:|
| M4 top-decile cutoff | 0.8737398492744993 |
| Near-park cells (≤500 m) | 537 |
| Near-park cells in top 254 | 0 |
| Maximum near-park score | 0.8696487759284656 |
| Difference | 0.004091073 |
| Minimum park distance in top 254 | 638.2027978 m |
| Top cells at 1,000 m cap | 174/254 |
| Top population | 1,539,790.68 |
| Top area | 63.412 km² |

Counterexample `JKT_R056_C048`: LST **45.58 °C**, population **6,971.49**,
park distance **487.960 m**, M4 score **0.869648776**, rank **274**; **236/254**
top cells are cooler. The text describes this as an arithmetic/construct
property, not evidence that parks are unimportant.

## 7. LISA primary convention and sensitivity

Adopted primary: **two-sided local Moran, 9,999 permutations, BH q = 0.05**.

Primary M4 counts:

- Significant: **493**
- HH: **252**
- LL: **227**
- HL: **7**
- LH: **7**
- Not significant: **2,042**

Independent `libpysal`/`esda` recomputation matched the saved p-values exactly
(maximum absolute difference 0.0) and the saved BH labels exactly.

Sensitivity:

| Tail | Permutations | Correction | Significant | Changed vs primary |
|---|---:|---|---:|---:|
| Two-sided | 9,999 | BH | 493 | 0 |
| Two-sided | 999 | BH | 496 | 65 |
| Directed | 999 | BH | 663 | 170 |
| Directed | 9,999 | BH | 687 | 194 |
| Two-sided | 9,999 | BY | 234 | 259 |
| Directed | 9,999 | BY | 284 | 209 |
| Directed | 999 | BY | 0 | 493 |

The BY/999 zero is a resolution artifact: minimum attainable p = 0.001 is above
the BY threshold ≈ 1.97 × 10⁻⁵. No p=0 claim is made.

Global Moran's I: M1 **0.671106**, M2 **0.654015**, M3 **0.664421**, M4
**0.593025**; expected value **−0.000395**; `p_sim = 0.001` at 999 permutations
(resolution limit).

## 8. Selection profile

| Group | n | Population | Mean LST | Mean NDVI | Mean coverage | Mean snap |
|---|---:|---:|---:|---:|---:|---:|
| Included | 2,536 | 10,519,840.5 | 41.486 °C | 0.315 | 0.940 | 49.98 m |
| Excluded | 229 | 463,696.6 | 40.283 °C | 0.365 | 0.821 | 98.81 m |

Excluded share: **8.28%** of grids and **4.22%** of modelled population. City
distribution: East 96, North 77, South 28, West 22, Central 6.

## 9. Scenario envelope

At the 10% budget: aggregation **0.881**; park threshold **0.521–0.682**;
weights **0.868–0.954**; QA exclusions **0.969–0.996**; missing park distance
**0.906**; joint factorial **0.583–0.728**; normalisation **0.734–0.814**;
population definition **0.347–0.977**; route policy **0.420–1.000**; thermal
support **1.000**; land cover **0.782**.

## 10. Engineering and references

- RC2 clean-checkout: **236 tests + 7 subtests**, 0 failures/errors/skips.
- RC1 and RC2 receipts: **9/9** under canonical Git-blob SHA-256.
- Standard/remediation manifests: **69/69** and **80/80** relative paths.
- 63-table replay: maximum numeric difference **0.0**.
- Model specification RC1 vs RC2: byte-identical.
- Claim C27 (Landsat scene/task/AOI lineage) remains technically BLOCKED; the
  release record documents editorial acceptance of the restricted preprint
  interpretation without changing that technical status.
- References: **67 cited** from a 67-entry database. Of the 67 cited entries,
  **64 carry DOI metadata** and **3 are no-DOI** items (Oke's 1984 book, the
  OpenStreetMap snapshot, and project documentation). USGS DOI
  `10.5066/P9OGBGM6`; WorldPop DOI `10.5258/SOTON/WP00841`.

## 11. PDF consistency

- Submission candidate: **25 pages**; no banner, neutral footer, no undefined
  citations/references.
- Internal review: **25 pages**; concise internal identifier only.
- Supplement: **8 pages**; S1–S9, including 49 scenarios, six no-support cells,
  eligibility reconciliation and primary LISA table.
- One overfull hbox **2.03 pt** in the main PDF and **1.41 pt** in the
  supplement; neither is visible in the rendered pages.

| Final PDF | Pages | Bytes | SHA-256 |
|---|---:|---:|---|
| `Manuscript-submission-candidate.pdf` | 25 | 2,426,183 | `72E4E50B60716408D3AE60A66DA1D422BD1A19E42D62F3D0A72660EB7553A986` |
| `Manuscript-internal-review.pdf` | 25 | 2,426,719 | `234BC4F7780D49A73844E4390B3E5FF04BFBB6B4C7876E2C6EDF2B1EBA0AB47B` |
| `Supplementary-submission-candidate.pdf` | 8 | 801,426 | `9CD990B91FDC94DAD04D5CE5663D42CD80920C8E9ECEC8908387133ACE096A58` |
