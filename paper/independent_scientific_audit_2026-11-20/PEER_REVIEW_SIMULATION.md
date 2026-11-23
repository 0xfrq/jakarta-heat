# Peer Review Simulation

**Manuscript:** *From Thermal Hotspots to Spatial Priorities: Attribution and
Sensitivity of Urban Heat Screening in Jakarta*
**Reviewer stance:** independent, skeptical, methods-focused
**Recommendation:** **Major revision** (not reject; the core is salvageable)
**Predicted decision at a methods/urban-climate journal:** major revision, with
a second review required because of the Table 7 defect and construct issues.

---

## 1. Summary for the editor

The manuscript asks a useful and under-examined question: how do priority
rankings change when LST and vegetation are supplemented with population, age
count and modelled park access, and how much of the change is attributable to
each construct? The authors are unusually candid about the mechanical park
cutoff, the age-count collinearity and the LISA convention sensitivity. The
screening/sensitivity framing is appropriate.

However, the central attribution table is internally inconsistent: it mixes
Jaccard values computed against M3 with values computed against M4 while stating
that all values are M4-relative. The error is material because the paper’s
argument about park dominance depends on which comparison is being described.
The construct itself is also not a validated vulnerability index; the age term is
a population count and the park term is a candidate proxy. The paper can be
salvaged by correcting the table, relabelling M4, pre-specifying LISA and
tightening the claim scope.

---

## 2. Major concerns

### M1. Table 7 mixes M3- and M4-relative Jaccard values

**Concern.** The caption says “reference is M4” and “Jaccard is overlap with the
M4 top decile”, but the reweighting/age/park rows come from
`matched_weight_comparison.csv`, whose baseline is M3. Exact independent values:

- reweighting: 0.961 vs M3, **0.423 vs M4**;
- age swap: 0.984 vs M3, **0.419 vs M4**;
- park addition: 0.490 vs M3, **0.861 vs M4**;
- park+reweighting: 0.415 vs M3, **0.977 vs M4**;
- age+park: 0.499 vs M3, **0.847 vs M4**.

**Why it matters.** The table currently tells a coherent M3-relative
incremental story but labels it as M4-relative. A reader trying to reproduce the
numbers from the stated reference will fail. It also weakens the paper’s
credibility precisely where it is strongest (transparency about model change).

**Required revision.** Split into Table 7a (incremental effects relative to M3)
and Table 7b (construct/ablation comparisons relative to M4), or label every row
with its baseline. Update the text and claim-evidence matrix. Do not leave the
caption as is.

**Revision status:** corrected in the current manuscript. Table 7 is
M3-relative, Table 8 is M4-relative, and the Jaccard/retention wording has been
fixed. This concern is retained as a record of the review, not as an open
release blocker.

### M2. M4 construct validity

**Concern.** M4 mixes a heat hazard, vegetation, an age count and a park
distance. The age count is nearly collinear with total population
(ρ=0.9995); the count swap leaves the top decile almost unchanged (J=0.977),
while the share swap changes it substantially (0.347). The park term dominates
85.46% of absolute rank movement and mechanically excludes all 537 near-park
cells from the top 254. M4 is therefore not an age-vulnerability model and not a
balanced heat-inequality index.

**Why it matters.** The title and abstract could be read as claiming a general
“spatial priorities” method; a policy reader may treat the top decile as a
vulnerability map. The paper must be unambiguous that M4 is a provisional
screening index.

**Required revision.** Adopt Option A (retain/relabel) for this manuscript:
rename M4 as a provisional heat–population–park-deficit screening index; remove
age-vulnerability and park-inequality implications; show near-park hot cells;
state the 85.46% is a descriptive model-change share. Plan Option B (separate
heat+population, age-share, park-access models) for future work.

### M3. LISA primary convention and inference

**Concern.** The manuscript calls directed/999/BH “provisional” and reports a
range, which is honest. But 999 permutations give a minimum p=0.001, and BY/999
yields zero significant cells purely because the threshold is below the
resolution. The significant count ranges from 0 to 687. A reader may still take
the 663 map as a confirmatory cluster result.

**Why it matters.** Local inference is a central part of the paper’s
“uncertainty” claim; if the primary convention is not pre-specified, the cluster
narrative is unstable.

**Required revision.** Pre-specify a primary convention. Recommended:
directed/9,999/BH, with directed/999/BH as continuity, two-sided/9,999/BH and
BY/9,999 as sensitivity. Report the full range in the abstract/discussion. Do not
use BY/999 as evidence of no clustering.

### M4. RS-01 lineage and the 2024 label

**Concern.** The thermal layer has no scene IDs, dates, task IDs or AOI hash.
The scene manifest is header-only; the GeoTIFF tags are empty. The 2024 label is
a declared recipe period, not verified acquisition. The manuscript mostly says
this, but “2024” is used as shorthand throughout.

**Why it matters.** A reviewer may read the paper as a verified 2024 heat
snapshot. It is not; it is a declared-period composite combined with a 2026
network.

**Required revision.** Use “declared 2024 thermal period” consistently; repeat
the restriction in the abstract, Methods, Figure 1 caption and Data Availability;
obtain a signed claim restriction or recover the lineage.

### M5. Park access is a candidate proxy, not verified public access

**Concern.** 1,015 candidates; 0 verified public access; 0 verified entrances;
1,015 unresolved; 980 unknown. The baseline has 226 missing routes; the
conservative scenario 407. The positive-tag stress test has only 10 destinations
and saturates 2,482 cells at the cap. The OSM snapshot is 2026, not 2024.

**Why it matters.** The park term is the dominant model component. If the
destinations are not public or the network is wrong, the priority map changes
materially (J=0.420 in the positive-tag stress).

**Required revision.** Keep the candidate-proxy label in every table/figure;
avoid “public park access” and “park inequality”; report the stress range; add
the near-park hot-cell table; state that field verification is required before
policy use.

### M6. Common subset and selection bias

**Concern.** The common set is 2,536 of 2,765 cells; 229 excluded, 4.2% of
population; excluded cells are cooler, greener, more peripheral. 18/277
full-thermal M1 top cells are lost; 13 route-missing cells could enter the top
254.

**Why it matters.** The common-set map is not Jakarta-wide. A reader may treat
the top decile as citywide.

**Required revision.** Show excluded cells on every priority map; report the
selection profile; use “five mainland cities under the common-set configuration”
rather than “Jakarta”. Keep the 13-cell bound in the limitations.

### M7. Novelty is incremental and conditional

**Concern.** The combination of LST, age and park access has precedent
(Sidiqui 2022; Kim & Kwak 2026; Fung 2024; Sobhaninia 2025). The manuscript
correctly rejects “first integrated framework”, but the abstract’s contribution
sentence may still sound like a new method. The targeted review is not
systematic.

**Why it matters.** Reviewers will ask “what is new?” The answer must be the
attribution/uncertainty audit and negative findings, not the combination.

**Required revision.** State the contribution in one precise paragraph:
“We quantify how priorities change across nested screening models, decompose the
M3→M4 change, and report negative findings about age-count redundancy and the
mechanical park cutoff.” Do not use “novel framework” or “first”.

### M8. Policy/health interpretation

**Concern.** The paper does not model health outcomes or intervention effects,
and says so. But “priority” language can still be read as a policy ranking.

**Why it matters.** A policy reader may treat the top decile as a budget
allocation.

**Required revision.** Keep the screening/field-verification framing; add a
sentence in the Discussion that the map cannot rank interventions without
cooling-effectiveness, cost and access data.

---

## 3. Minor concerns

1. **Sidiqui et al. context.** Table 1 calls it a “GIS-based urban case”; it is
   Greater Geelong, Australia. Add the location to avoid confusion with Jakarta.
2. **Reference count.** `References.bib` has 62 entries; 61 are cited. Vargas
   Molina et al. (2026) is in the matrix but not cited. Either cite it in the
   climate-shelter/access paragraph or remove it from the matrix/database.
3. **Reference capitalization.** `OpenStreetMap`, `Jakarta`, `R2025A` are
   lowercased in some `.bbl` entries because they are not braced. Fix the bib
   fields for publication quality.
4. **Natural logarithm.** Define \(\log\) as the natural logarithm; the code uses
   `log1p`. The min–max normalisation is invariant to log base, but the formula
   should be unambiguous.
5. **Table 7 footnote.** “Retained counts cells in both the scenario and M4 top
   sets” is false for the M3-relative rows. Fix with the table split.
6. **Data availability.** The manuscript says a clean RC1 checkout has one
   test failure; RC2 fixes it. State whether the manuscript uses RC1 (frozen) or
   RC2 (portable), and do not claim a failure that has been fixed without
   calling it historical.
7. **M4 top-decile language.** “No near-park cell enters” is correct; always add
   “under the observed inputs and provisional formula.”
8. **Figure 4.** The median signed change (−14) and median absolute change (239)
   are both reported; keep the distinction.
9. **Table 8 “peripheral.”** The evidence is mean snap distance; say “more
   peripheral, as measured by network snap distance” rather than implying a
   general geographic periphery.
10. **Abstract length.** The abstract is long and dense; a 250–300 word version
    would be more readable, but this is stylistic.

---

## 4. Anticipated reviewer objections and defensible responses

| Objection | Defensible response | Residual risk |
|---|---|---|
| “This is just another composite index with arbitrary weights.” | We agree it is a provisional screening index; we do not claim validation or superiority. The contribution is the attribution/sensitivity audit, and the weights are explicitly provisional. | Reviewers may still see the paper as incremental. |
| “The park term mechanically excludes near-park cells; the headline is an artifact.” | Yes; we disclose the cutoff arithmetic and present it as a construct property, not an empirical park effect. The near-park hot-cell example is included. | The paper must not imply parks are unimportant; the current text is careful. |
| “Age count is just population; there is no age vulnerability.” | Correct; we report the near-collinearity and the count-vs-share distinction. M4 is not an age-composition model. | The title/abstract must not imply age vulnerability. |
| “LISA clusters are not robust.” | We report the full convention range and avoid causal/confirmatory claims. | The primary convention must be pre-specified. |
| “The 2024 thermal data are not verified.” | Correct; 2024 is a declared recipe period. We restrict the claim. | A signed restriction is needed. |
| “OSM 2026 cannot represent 2024 access.” | Correct; this is a mixed-period candidate proxy. We make no temporal claim. | Reviewers may ask for a historical network; it is unavailable. |
| “Public park access is unverified.” | Correct; 0 verified access/entrances. We use a candidate proxy and stress tests. | Field verification is needed for a stronger claim. |
| “The common subset is not Jakarta-wide.” | Correct; we report the 229 excluded cells and avoid citywide claims. | The title/abstract should not overgeneralize. |
| “The paper is not novel.” | The contribution is the attribution/uncertainty audit and negative findings; we do not claim a new framework. | Novelty remains conditional on the targeted review. |
| “Table 7 is wrong.” | This is a real defect; fix it before resubmission. | Fatal if left uncorrected. |

---

## 5. What would make the paper publishable

1. Correct/split Table 7 and update the text; this is non-negotiable.
2. Adopt Option A for M4 and remove residual age/park implications.
3. Pre-specify LISA primary and report the full range.
4. Sign the RS-01 claim restriction or recover lineage.
5. Keep the candidate-proxy and common-subset language in every section.
6. Sharpen the novelty statement; add the Geelong context and resolve the
   Vargas citation.
7. Add the corrected attribution table and near-park hot-cell table to the
   supplement/main text.
8. Have the coordinator sign D1–D12 and run a final independent re-audit.

---

## 6. Recommendation

**Major revision.** The paper has a defensible core: a transparent, reproducible
audit of how a Jakarta heat-screening index changes under demographic and
accessibility assumptions, including negative findings. It is not a validated
vulnerability or policy-effect paper, and it should not be presented as one. The
Table 7 defect and Jaccard wording are corrected in the current revision. D4,
D10, RS-01 and human approvals still need resolution before any public release.
After those, the paper can be a credible **CONDITIONAL PASS** preprint, but not
“ready for publication” without human scientific approval.
