# Independent Scientific Audit — Jakarta Heat Inequality Mapper

**Audit date:** 20 November 2026 (WIB)
**Auditor role:** independent senior research scientist, geospatial methodology
reviewer, statistical auditor, and critical peer reviewer
**Manuscript:** *From Thermal Hotspots to Spatial Priorities: Attribution and
Sensitivity of Urban Heat Screening in Jakarta*
**Workspace:** `D:\jakarta-heat-paper\paper\zenodo_preprint`
**Frozen reference:** RC1 `3b8ed05be92c35bbb2b3a617688540ee856b11c8`
**Audit workspace:** `D:\jakarta-heat-paper\paper\independent_scientific_audit_2026-11-20`
**Overall recommendation:** **HOLD — major revision required before public
preprint release**

---

## 1. Executive assessment

The manuscript is a serious, unusually transparent, and largely reproducible
screening study. Its strongest features are the explicit separation of construct
from accuracy, the disclosure of the mechanical park-deficit behaviour, the
near-collinearity finding for the age count, the scenario envelope, and the
honest treatment of LISA conventions. The arithmetic that underpins the main
results is reproducible from the frozen RC1 tables; I independently recomputed
the model scores, ranks, Jaccard overlaps, Shapley decomposition, cutoff
arithmetic, selection profile, scenario-family ranges, Moran's I and LISA counts.

The manuscript is **not** ready for public preprint release in its current form.
One material numerical/labelling defect was found in the central attribution
table: **Table 7 mixes Jaccard values computed against M3 with values computed
against M4**, while its caption and footnote state that every comparison is
against M4. The text around the table repeats the same confusion. The corrected
M4-relative values are materially different (for example, park addition is
Jaccard 0.861 against M4, not 0.490), and the table must be split or relabelled.
The scientific conclusion that the park term dominates rank movement survives
because it is independently supported by the Shapley decomposition and by the
M3-relative incremental comparisons, but the current table cannot be published as
written.

Beyond that defect, the main unresolved issues are construct validity (M4 is a
provisional screening index, not an age-vulnerability or health-risk model), the
absence of verified Landsat acquisition lineage (RS-01), the convention
dependence of LISA, unverified public park access, mixed 2024/2026 reference
periods, and the conditional nature of the 2,536-cell common sample. The
manuscript discloses most of these limitations, but several scientific decisions
remain unsigned and the claim structure needs to be tightened.

**Disposition:** the manuscript is a **credible exploratory screening and
methods/sensitivity draft**, not a validated heat-vulnerability or policy-effect
paper. The appropriate release decision is **HOLD**, with a clear path to
**CONDITIONAL PASS** after the Table 7 correction, M4 relabelling, LISA
pre-specification, and signed RS-01 claim restriction.

---

## 2. Scope, evidence and limits

### 2.1 Evidence reviewed

- RC1 independent re-audit and decision records:
  `RC1_REAUDIT_REPORT.md`, `RC1_ISSUE_CLOSURE_MATRIX.csv`,
  `RC1_RELEASE_GATE.md`, `RC1_SCIENTIFIC_DECISIONS.md`,
  `RC1_NOVELTY_EVIDENCE.md`, `RC1_REMAINING_TASKS.md`,
  `RC1_VERIFICATION_LOG.md`, `RC1_EXECUTIVE_SUMMARY.md`.
- RC1 integration evidence: `handoff/RC1_HANDOFF.md`,
  `handoff/RC1_VERIFICATION.md`, `docs/RC1_REPRODUCE.md`,
  `docs/integration_manifest.json`, `docs/model_specification.json`,
  `docs/spatial_inference_spec.md`, `docs/park_destination_policy.md`,
  `docs/population_aggregation_method.md`,
  `docs/demographic_mask_semantics.md`.
- RC1 tables: `data/processed/modeling/`, `outputs/tables/`,
  `outputs/remediation/tables/`.
- RC1 remote-sensing rasters and metadata:
  `data/processed/remote_sensing/`,
  `data/processed/remote_sensing_remediated/`,
  `docs/landsat_metadata.json`,
  `docs/remote_sensing_export_manifest.json`,
  `docs/remote_sensing_scene_manifest.csv`.
- Manuscript and supplement: `input/Manuscript.tex`,
  `input/Supplementary.tex`, all tables and figures,
  `CLAIM_EVIDENCE_MATRIX.csv`, `LITERATURE_MATRIX.md`,
  `SOURCE_PROVENANCE.md`, `FIGURE_TABLE_REGISTER.md`,
  `MANUSCRIPT_STATUS.md`, `REVISION_LOG.md`.
- RC2 engineering state (read-only): branch `integration/rc2`, HEAD
  `3439f38d38e9b7e844524a59d034bdf8711366d1`; handoff and receipts were
  inspected but RC2 was not substituted for RC1.

### 2.2 Independent computations performed

I recomputed, from the frozen RC1 CSVs rather than from manuscript tables:

- M1–M4 scores from `merged_grid.csv` using the documented p5–p95
  normalisation, park cap and weights. Maximum absolute score difference from
  the saved `priority_models.csv`: **0.0** for all four models.
- Ranks with the documented tie-break (unclipped score, then grid ID). Rank
  mismatches: **0** for all four models.
- Top-decile sets (254 cells), pairwise Jaccard values, Spearman/Kendall
  correlations and rank displacement.
- The exact three-factor Shapley decomposition and the sum-to-rank-gain
  identity.
- The M3-relative and M4-relative Jaccard values for the matched-weight
  scenarios.
- The M4 cutoff, the maximum score among the 537 near-park cells, the minimum
  park distance in the top 254, and the near-park example cell.
- The selection profile and city distribution of excluded cells.
- Scenario-family Jaccard ranges from the scenario top-set table.
- Moran's I and LISA with `libpysal` Queen weights, row standardisation, island
  removal, 999 and 9,999 permutations, directed and two-sided alternatives,
  BH and BY corrections.

Evidence files are in
`paper/independent_scientific_audit_2026-11-20/evidence/`; scripts are in
`.../scripts/`.

### 2.3 Limits of this audit

- I did not recover the original Landsat scene/task/AOI records; no such records
  exist in the available artifacts. RS-01 remains an external block.
- I did not perform a field audit of park access, entrances or connector
  permissions.
- I did not re-run the entire RC1 pipeline from raw rasters; I recomputed from
  the frozen processed tables and, for LISA, from the frozen grid geometry and
  scores.
- I did not independently verify the raw WorldPop source rasters; the
  demographic support evidence was inspected from the frozen processed tables
  and the RC1 audit.
- I did not perform a systematic literature review; the novelty assessment is
  targeted and conditional.
- I did not modify, commit or upload the manuscript or data.

---

## 3. Construct validity of M4 (Priority A, D4)

### 3.1 What M4 is

The implemented M4 is

\[
S_4 = 0.30\,n(LST) + 0.20\,[1-n(NDVI)]
    + 0.25\,n(\log(1+C+E))
    + 0.25\,\min(d,1000)/1000,
\]

where \(n(\cdot)\) is p5–p95 min–max normalisation on the common sample,
\(C+E\) is the count of children aged 0–14 plus adults aged 65+, and \(d\) is
the modelled candidate-park network distance. Weights are provisional and
unsigned.

### 3.2 Verified empirical findings

1. **Park addition dominates rank movement.** The exact three-factor Shapley
   shares of absolute M3→M4 rank movement are **85.461% park addition,
   13.249% reweighting, 1.289% age substitution**. The per-cell Shapley
   contributions sum to the rank gain with maximum absolute error
   \(2.3\times10^{-13}\). This is a descriptive decomposition, not a causal
   effect.
2. **Age count is nearly collinear with total population.** Spearman
   \(\rho=0.999479\). Replacing the age count with total population leaves the
   top decile almost unchanged (Jaccard **0.976654**, 251/254 retained).
   Replacing it with a vulnerable share changes the set substantially
   (Jaccard **0.347480**, 131/254 retained). Child share is 0.451429; elderly
   share is 0.391781.
3. **The age term is not age composition.** The vulnerable share is nearly
   constant (mean 0.2955, SD 0.0073, 5th–95th 0.2894–0.3016), and its
   correlation with LST is essentially zero (Spearman 0.0057). The top-M4
   vulnerable share range is only 1.2 percentage points.
4. **The park term mechanically determines the top decile under observed
   inputs.** The M4 top-decile cutoff is **0.873739849**. The maximum score among
   the 537 common cells within 500 m of a candidate park is **0.869648776**.
   The cutoff exceeds that maximum by **0.004091**, so **0 of 537** near-park
   cells enter the top 254. The closest top cell is **638.2 m** from a
   candidate park; **174/254** top cells are at the 1,000 m cap. The example
   cell `JKT_R056_C048` (North Jakarta) has LST 45.58 °C, population 6,971,
   park distance 487.96 m, M4 score 0.869649 and rank 274; 236/254 top cells
   are cooler. This is a property of the additive index and observed inputs,
   not an empirical discovery that parks are unimportant.
5. **The park term is not the whole index.** A park-only index has top-decile
   Jaccard **0.028340** with M4 (14/254); a no-park variant has **0.422969**;
   a heat-only variant has **0.384196**; an equal-weight variant has
   **0.867647**. M4 is not merely a park map, but it is also not a balanced
   heat-inequality index.

### 3.3 Interpretation

M4 is scientifically defensible **only as a provisional composite screening
index**. It is not a validated vulnerability index, not an age-vulnerability
model, and not a health-risk model. The age term is effectively a population
count; the park term is an access proxy with a mechanical threshold effect. The
85.46% Shapley share is a property of the model change (new term, 0.25 weight,
wide 0–1 range), not a real-world causal share.

The manuscript already contains most of this language. The remaining risks are:

- the abstract and title may still be read as claiming a general “spatial
  priorities” method that is more validated than it is;
- Table 7 currently mislabels M3-relative values as M4-relative, which
  undermines the transparency that the rest of the paper tries to achieve;
- the phrase “age vulnerability” must not reappear in the abstract,
  discussion, figure captions or policy implications unless the estimand is a
  share and the model is refitted accordingly.

### 3.4 Options A/B/C

| Option | Description | Advantages | Limitations | Required analyses | Manuscript implications | Risk |
|---|---|---|---|---|---|---|
| **A. Retain M4, relabel** | Keep formula; rename to “provisional heat–population–park-deficit screening index”; drop age-vulnerability and park-inequality implications; disclose cutoff and near-park cells | Preserves all results; honest; minimal reanalysis; matches current evidence | Still a composite with arbitrary weights; age term is redundant with population; park term still dominates | Recompute Table 7 with correct baselines; add near-park hot-cell table/figure; add explicit “not age composition” statement | Retitle sections/abstract claims; revise Table 7 and discussion; keep limitations | Medium: readers may still treat the map as a vulnerability map unless labels are prominent |
| **B. Separate objectives** | Define M4a heat + population exposure; M4b age composition (share with population control); M4c park access; report separately | Scientifically cleanest; avoids forcing one composite to answer three questions; makes estimands explicit | Requires new models, rankings, sensitivity, figures; may weaken the single “M4” narrative; more work | Refit and rerank M4a–M4c; new top-set comparisons; new Shapley/ablation; update figures/tables | Major rewrite; likely a different paper | Low scientific risk, high production risk |
| **C. Revise M4 formula** | Change weights, cap, distance decay or normalisation; rerun everything | Could reduce mechanical dominance; may produce a more balanced index | Arbitrary without theory; new results may still be dominated by park; destroys comparability with RC1; no validation | Full reanalysis, new sensitivity envelope, new audit | Major rewrite; not appropriate for this preprint | High: could create a new, equally arbitrary artifact |

**Recommendation for this manuscript:** **Option A**, with two mandatory
conditions: (i) correct and split Table 7; (ii) remove every remaining
age-vulnerability or park-inequality implication, and foreground the mechanical
cutoff. **Option B** is the stronger long-term research design and should be the
next study, not a silent change to this one. **Option C** is not recommended for
the current preprint because it would be an unvalidated re-specification.

---

## 4. LISA statistical validity (Priority B, D10)

### 4.1 What was verified

Using `libpysal.weights.Queen.from_dataframe` on the 2,536-cell common grid,
removing the single island `JKT_R013_C019`, row-standardising, and running
`esda.Moran_Local` with seed 42:

| Check | Independent result | Manuscript/RC1 |
|---|---:|---:|
| Joined common cells | 2,536 | 2,536 |
| Island removed | `JKT_R013_C019` | same |
| Tested cells | 2,535 | 2,535 |
| Directed Queen edges | 18,368 | 18,368 |
| Mean neighbours | 7.245759 | 7.245759 |
| Moran M1 | 0.671106279 | 0.671106279 |
| Moran M2 | 0.654014824 | 0.654014824 |
| Moran M3 | 0.664420702 | 0.664420702 |
| Moran M4 | 0.593024954 | 0.593024954 |
| M4 directed/999/BH significant | 663 | 663 |
| M4 two-sided/999/BH significant | 496 | 496 |
| M4 directed/9,999/BH significant | 687 | 687 |
| M4 two-sided/9,999/BH significant | 493 | 493 |
| M4 directed/999/BY significant | 0 | 0 |
| M4 directed/9,999/BY significant | 284 | 284 |
| M4 two-sided/9,999/BY significant | 234 | 234 |

The saved M4 LISA p-values match the independent recomputation exactly
(maximum absolute difference 0.0), and the saved FDR labels match exactly.

### 4.2 What the conventions mean

- **Directed vs two-sided.** Directed testing is appropriate for the stated
  hypothesis of positive spatial autocorrelation (high–high and low–low
  clustering). Two-sided testing is a broader sensitivity that also changes
  which local outliers are labelled.
- **999 vs 9,999 permutations.** At 999 permutations the minimum attainable
  \(p\)-value is 0.001. This is a resolution limit, not \(p=0\). At 9,999 the
  resolution is 0.0001 and labels are more stable.
- **BH vs BY.** BH controls FDR under independence or positive dependence; BY
  is conservative under arbitrary dependence. At 999 permutations, the BY
  threshold is below the minimum attainable \(p\)-value, so the zero count is a
  resolution artifact. At 9,999, BY yields 284 directed and 234 two-sided
  significant cells.
- **Testing family.** The family is all non-island cells in each preselected map
  separately; it is not a family across all interactive selections.

### 4.3 Recommended primary convention

**Primary:** directed, **9,999 permutations**, **BH** at \(q=0.05\), applied
separately to each model map (M1–M4), with the full label set and counts
reported.

**Secondary/sensitivity:** directed/999/BH (RC1 continuity), two-sided/999/BH,
two-sided/9,999/BH, directed/9,999/BY, two-sided/9,999/BY.

**Do not use** BY/999 as evidence of no clustering. **Do not claim** that the
directed/999/BH result is confirmatory without acknowledging the Monte Carlo
resolution. If the team prefers to retain 999/BH as the primary for continuity,
the paper must label it **exploratory** and avoid confirmatory language; the
9,999 results must remain in the abstract or main results, not only in a
supplementary table.

The current manuscript calls directed/999/BH “provisional” and reports the
range; that is honest but not yet a pre-specified primary. The recommendation is
a scientific decision for the coordinator, not something this audit can sign.

---

## 5. Landsat and source provenance (Priority C, RS-01)

### 5.1 What is verified

- The Landsat 9 Collection 2 Level-2 GeoTIFF exists and is readable:
  1,058 × 1,042 pixels, EPSG:32748, 30 m, five bands (`lst_c`, `ndvi`,
  `lst_unc_k`, `lst_obs`, `lst_valid`), nodata −9999.
- The delivered grid table has 2,765 rows and zero missing LST/NDVI values.
- The local raster-to-grid aggregation is reproducible; the delivered values
  and hashes are recorded in the export manifest.
- The intended recipe is documented: QA_PIXEL bits 0–5 and QA_RADSAT = 0;
  ST_B10 scaling to °C; SR_B4/SR_B5 NDVI; per-pixel median; 30 m export.
- Annual clear-observation counts are available; the composite is a clear-sky
  morning median.

### 5.2 What is missing

- The scene manifest is **header-only (0 rows)**. This means records are
  unavailable, not that zero scenes were acquired.
- No scene IDs, acquisition dates, WRS path/row, product IDs or task IDs are
  present.
- `processing_date` and `task_id` are null.
- The AOI asset geometry/hash cannot be tied to the historical GEE run.
- The GeoTIFF has no scene/date/task metadata tags.
- Monthly/seasonal support cannot be reconstructed from the median raster.
- Six historical OSM requests failed; no temporal comparison is possible.

### 5.3 Narrowest defensible claim

> The thermal layer is a **declared 2024 clear-sky morning median composite**
> derived from Landsat 9 Collection 2 Level-2 using the intended Google Earth
> Engine recipe. The local raster-to-grid aggregation is reproducible from the
> frozen export. The original scene/task/AOI lineage is unavailable; the 2024
> label is a recipe period, not an independently verified acquisition history.
> No annual, seasonal, trend, air-temperature or personal-exposure claim is
> supported.

This is the claim the manuscript should make. It currently does so in the
Methods and Figure 1 caption, but the abstract and conclusion should repeat the
“declared recipe period” qualification and never say “verified 2024 data”.

### 5.4 To close RS-01

Recover and archive: scene/product IDs; UTC acquisition dates; WRS path/row;
L2SP flags; task IDs and completion timestamps; exact AOI geometry and hash;
monthly clear-observation counts; and the original recipe/task JSON. If this is
impossible, a signed claim restriction is required. The latter is scientifically
acceptable for an exploratory preprint but must be explicit in the cover letter,
abstract, Methods and data availability.

---

## 6. D1–D12: audit summary

Detailed recommendations are in
`SCIENTIFIC_DECISION_RECOMMENDATIONS.md`. The short disposition is:

| ID | Decision | Audit status | Human approval? |
|---|---|---|---|
| D1 | Mixed 2024/2026 reference periods | **Conditionally acceptable** as mixed-period proxy; no 2024 access/2026 heat claim | Yes |
| D2 | Historical OSM unavailable | **Accept claim withdrawal**; no temporal stability claim | Yes |
| D3 | Null vs zero support semantics | **Accept technical evidence**; do not impute six null cells | Yes (formal) |
| D4 | M4 construct/weights | **HOLD**; Option A minimum, Option B preferred long-term | Yes |
| D5 | Count vs share | **Define count-based exposure as primary**; share separate | Yes |
| D6 | Hybrid vs fractional aggregation | **Conditional**; report both; fractional preferred for additive accounting | Yes |
| D7 | Thermal support threshold 0.50 | **Retain provisional** with 0.25/strict sensitivity | Yes |
| D8 | Park access/route assumptions | **Candidate proxy only**; no public/legal claim | Yes |
| D9 | Common set 2,536 | **Accept for comparison**; report full-area/excluded; no Jakarta-wide | Yes |
| D10 | LISA convention | **HOLD**; recommend directed/9,999/BH primary, full range | Yes |
| D11 | Dynamic World categorical deferral | **Accept deferral**; no categorical claim | Yes |
| D12 | Novelty/claim scope | **Conditional**; attribution/uncertainty contribution only | Yes |
| D13 | Final scientific release | **HOLD** | Yes |

No decision is approved by this audit. The audit recommends, but the coordinator
must sign.

---

## 7. Independent quantitative verification

Full details are in `QUANTITATIVE_REPRODUCIBILITY_AUDIT.md`. Key results:

- Scores: maximum absolute difference **0.0** for M1–M4.
- Ranks: **0** mismatches under the documented tie-break.
- Top-decile budget: **254**.
- Jaccard M1–M4: **0.384196** (141/254).
- Mean absolute M1–M4 rank shift: **307.388** (median 239; p90 696.5).
- M3–M4 Jaccard: **0.411111** (148/254).
- Shapley: **85.461% / 13.249% / 1.289%**; sum identity error \(2.3\times10^{-13}\).
- M4 cutoff **0.873739849**; near-park max **0.869648776**; **0/537**;
  top minimum **638.2 m**; **174/254** at cap.
- Selection: 229 excluded; 8.28% of grids; 4.22% of population; included vs
  excluded LST 41.486 vs 40.283 °C; NDVI 0.315 vs 0.365; snap 49.98 vs
  98.81 m.
- LISA: 663/496/687/493/0/284/234; independent recomputation exact.
- Scenario families: aggregation 0.881; park threshold 0.521–0.682; weights
  0.868–0.954; QA 0.969–0.996; missing park distance 0.906; joint 0.583–0.728;
  normalisation 0.734–0.814; population 0.347–0.977; route 0.420–1.000;
  thermal 1.000; land cover 0.782.

**Discrepancy:** Table 7 mixes two baselines. The exact M4-relative values are:

| Scenario | M4-relative J | Shared/254 | M3-relative J | Shared/254 |
|---|---:|---:|---:|---:|
| Reweighting only | **0.422969** | **151** | 0.961390 | 249 |
| Age swap only | **0.418994** | **150** | 0.984375 | 252 |
| Park addition only | **0.860806** | **235** | 0.489736 | 167 |
| Age + reweighting | **0.422969** | **151** | 0.953846 | 248 |
| Park + reweighting | **0.976654** | **251** | 0.415042 | 149 |
| Age + park | **0.847273** | **233** | 0.498525 | 169 |
| M3 | **0.411111** | **148** | 1.000000 | 254 |
| M4 | **1.000000** | **254** | 0.411111 | 148 |

The manuscript table's 0.961/0.984/0.490/0.415/0.499 values are **M3-relative**
and must not be described as overlaps with M4. This is the principal numerical
defect found in the audit.

---

## 8. Literature, novelty and publication integrity

The literature review is targeted and honest about its limits. The closest prior
work includes Sidiqui et al. (2022, Greater Geelong, Australia), Kim & Kwak
(2026, cooling-weighted park access for older adults), Fung et al. (2024,
social-vulnerability prioritisation), Sobhaninia et al. (2025, green
infrastructure siting review), Rizki et al. (2024, East Jakarta LST/NDVI), and
Varquez et al. (2020, Jakarta elderly heat mortality). The combination of LST,
age and park access is not novel; the manuscript correctly rejects a
combination-only novelty claim.

The defensible contribution is the **attribution and uncertainty audit**:
quantifying how priorities change across nested screening models, decomposing
the M3→M4 change, and reporting negative findings (age-count redundancy;
mechanical park cutoff). This is a methodological/empirical audit, not a new
algorithm or a validated vulnerability framework. The manuscript states this,
but the abstract’s “contribution” sentence and the title’s “spatial priorities”
could still be read as a stronger applied claim. A reviewer may ask for a
sharper distinction between “we audited a screening index” and “we produced a
validated priority map.”

**Novelty confidence:** conditional. The targeted review is not systematic;
absence of a closer study is not proof of novelty. The paper should not use
“first”, “novel framework”, or “validated” language.

Two literature-integrity details need correction or explanation:

- The manuscript says “61 bibliographic references”; the BibTeX file contains
  62 entries, with Vargas Molina et al. (2026) present but not cited. Either cite
  it in the climate-shelter/access paragraph or remove it from the citation
  database. The reference list currently has 61 cited entries.
- The Sidiqui et al. row in Table 1 should state **Greater Geelong, Australia**,
  not only “GIS-based urban case”; this matters for positioning, because the
  paper is not a Jakarta study. The manuscript text is accurate but the table is
  vague.

---

## 9. Manuscript and supplementary review

### 9.1 Strengths

- Clear research questions and an explicit screening (not health/causal) framing.
- Full mathematical specification of M1–M4, normalisation, Jaccard, Shapley,
  scenario design and LISA.
- Unusual transparency about the mechanical park cutoff and the age-count
  redundancy.
- Correct reporting of mixed periods, unverified access, missing routes,
  sample selection and LISA convention sensitivity.
- Figures are generated from RC1 data, not dashboard screenshots; maps show
  excluded cells.
- Claim-evidence matrix, literature matrix, provenance register and compilation
  report are substantive.
- The PDF compiled cleanly at the time of audit (23 pages; 6-page supplement);
  after the post-audit corrections it is 24 pages with a 7-page supplement, and
  still has no undefined citations or references.

### 9.2 Major concerns

1. **Table 7 baseline mixing** (critical; see §7).
2. **M4 construct**: the paper still needs an explicit, signed decision that
   M4 is a screening index, not an age-vulnerability or park-inequality model;
   the table error weakens this.
3. **LISA primary convention**: directed/999/BH is called provisional; the
   paper needs a pre-specified primary and a clear confirmatory/exploratory
   distinction.
4. **RS-01**: no scene/task/AOI lineage; the 2024 label is a declared period.
5. **Park access**: 0 verified public access/entrances; 1,015 unresolved;
   positive-tag stress test is not ground truth.
6. **Selection**: 229 excluded cells; common set conditional; no Jakarta-wide.
7. **Novelty**: incremental relative to prior multi-indicator/access work; the
   attribution/uncertainty framing is defensible but must be stated more
   sharply.
8. **Policy interpretation**: the top decile is a screening set, not an
   intervention ranking; the manuscript says this but the discussion could be
   firmer.

### 9.3 Minor concerns

- Define \(\log\) as natural logarithm.
- Table 7 footnote/source baseline; split or relabel.
- Reference capitalization (`OpenStreetMap`, `Jakarta`, `R2025A`).
- Vargas citation/reference count.
- Sidiqui study location.
- Data availability says RC1 clean checkout has one failure; RC2 engineering
  fixes it. Clarify whether the manuscript uses RC1 (frozen) or RC2 (portable),
  and do not claim a portability failure that has been fixed unless it is
  explicitly historical.
- The `M4` top-decile phrase “no near-park cell enters” is correct but should
  always be followed by “under the observed inputs and provisional formula”.
- Figure 4’s median signed vs median absolute distinction is correctly stated;
  keep it.

### 9.4 Supplementary review

The supplement is complete for the main sensitivity claims: data quality,
three-budget family sensitivity, city composition, LISA counts, exclusion map,
score distributions, park inventory and provenance. It is scientifically
consistent with the main text except for the same Table 7 issue (the supplement
does not repeat Table 7, so no additional numerical defect). The supplement’s
S6 provenance table is useful. The supplement could add the corrected Table 7
split and the exact M4-relative/M3-relative comparison once the main table is
fixed.

---

## 10. Claim status

The updated `CLAIM_EVIDENCE_MATRIX.csv` has 42 claims (39 VERIFIED,
2 PROVISIONAL, 1 BLOCKED). The one remaining BLOCKED claim is RS-01
(Landsat lineage).

- **C33 (VERIFIED)** states the M3-relative incremental values and the
  corresponding M4-relative values.
- **C39 (VERIFIED)** records that the Table 7/8 split has been completed:
  Table 7 is M3-relative, Table 8 is M4-relative, and no mixed-baseline table
  remains.

The matrix distinguishes:

- **M3-relative incremental effects** (0.961, 0.984, 0.490, 0.415, 0.499);
- **M4-relative construct/ablation effects** (0.423, 0.419, 0.861, 0.977,
  0.847);
- **M4 reference** (1.000);
- **M3 reference** (1.000).

---

## 11. Bottom line

**Scientific value:** moderate-to-high as a transparent exploratory screening
and sensitivity study; low as a validated vulnerability or policy-effect study.

**Reproducibility:** strong for the RC1 processed tables and LISA; conditional
for the raw Landsat lineage (RS-01) and raw WorldPop inputs. RC2 engineering
fixes the clean-checkout/receipt/manifest portability issues without changing the
model definitions or empirical outputs.

**Publication readiness:** **HOLD**. The Table 7 defect and Jaccard wording are
corrected in the current manuscript revision (Table 7 M3-relative; Table 8
M4-relative; 141/254 = 55.5% retention, Jaccard 0.384). The construct, LISA,
RS-01, access and selection issues remain disclosed but not signed. After M4
relabelling, LISA pre-specification and a signed RS-01 restriction, the
manuscript could move to **CONDITIONAL PASS** for a preprint, but not to
"ready for publication" without human scientific approval and a final
independent re-audit.

---

## 12. Recheck note (second audit pass)

On the second audit pass (20 November 2026), I re-ran the independent score,
rank, attribution, cutoff and LISA checks against the unchanged RC1 artifacts.
The results were identical to the first pass:

- M1-M4 scores: maximum absolute difference **0.0**.
- Ranks: **0** mismatches.
- Table 7 corrected M4-relative values: reweighting **0.422969/151**, age
  **0.418994/150**, park **0.860806/235**.
- M4 cutoff **0.873739849**; near-park maximum **0.869648776**; **0/537**.
- LISA M4 directed/999/BH **663**; two-sided **496**; directed/9,999/BH
  **687**; two-sided/9,999/BH **493**; BY/999 **0**; BY/9,999 **284/234**.
- Moran M1-M4 **0.671106 / 0.654015 / 0.664421 / 0.593025**.

The recheck itself did not change the manuscript. The subsequent revision has
corrected the Table 7 defect: Table 7 is now M3-relative, Table 8 is
M4-relative, and the Jaccard/retention wording has been fixed. The audit
conclusion remains **HOLD** only because D4, D10, RS-01 and human approvals
remain unresolved, and the corrected PDF still requires a final independent
re-audit.
