# Scientific Decision Recommendations — D1–D12

**Audit date:** 20 November 2026
**Frozen reference:** RC1 `3b8ed05be92c35bbb2b3a617688540ee856b11c8`
**Status:** recommendations only; **no decision is signed by this audit**

This document responds to `RC1_SCIENTIFIC_DECISIONS.md`. For each decision it
states the available evidence, alternatives, recommended resolution, confidence,
consequences and whether human approval is required. It does not silently change
the model, weights, thresholds, sample or manuscript.

---

## Summary table

| ID | Decision | Recommendation | Confidence | Human approval |
|---|---|---|---|---|
| D1 | Mixed 2024/2026 reference periods | Accept as mixed-period candidate proxy; prohibit 2024 access/2026 heat claims | High | Yes |
| D2 | Historical OSM unavailable | Accept claim withdrawal; no temporal stability claim | High | Yes |
| D3 | Null vs zero support semantics | Accept null/no-source semantics; do not impute six unsupported cells | High | Yes (formal) |
| D4 | M4 construct/weights | Retain and relabel M4 as a provisional exposure-oriented screening index (Option A); plan Option B for future work | High for A; medium for B | Yes |
| D5 | Count vs share | Define count-based exposure as primary; report share separately; do not call the count “age vulnerability” | High | Yes |
| D6 | Hybrid vs fractional aggregation | Report both; prefer fractional for additive count accounting; if hybrid remains primary, state non-additivity prominently | Medium-high | Yes |
| D7 | Thermal support threshold 0.50 | Retain 0.50 as provisional primary with 0.25/strict sensitivity; do not claim it is validated | Medium | Yes |
| D8 | Park access/route assumptions | Candidate proxy only; no public/legal access claim; baseline route is modelled and unvalidated | High | Yes |
| D9 | Common set 2,536 | Use for model comparison; report full-area and excluded cells; no Jakarta-wide claim | High | Yes |
| D10 | LISA convention | Recommend directed/9,999/BH primary with full sensitivity range; retain 999/BH as continuity | Medium-high | Yes |
| D11 | Dynamic World categorical deferral | Accept deferral; no categorical-area or tree-fraction claim | High | Yes |
| D12 | Novelty/claim scope | Claim attribution/uncertainty audit and negative findings; no “first” or “novel combination” | High (conditional) | Yes |
| D13 | Final release | **HOLD** until D1–D12, Table 7 correction and final audit | High | Yes |

---

## D1 — Reference periods (mixed 2024/2026)

**Evidence.** `docs/variable_reference_periods.csv` states LST/NDVI 2024,
WorldPop 2024 reference year, and OSM 2026-11-19. `claim_to_period_matrix.csv`
withdraws “actual 2024 usable public-park access” and “M4 improves health or
policy outcomes”. The Landsat scene manifest is empty; the 2024 thermal label is
declared by the intended recipe, not verified acquisition.

**Alternatives.**
1. Treat the study as a mixed-period candidate proxy (recommended).
2. Restrict to 2024 thermal/demographic patterns and omit the 2026 park term
   (would remove the core M4 comparison).
3. Attempt a historical OSM reconstruction (six requests failed; not feasible
   with current evidence).

**Recommendation.** Accept as a **mixed-period candidate proxy**. Use
“declared 2024 thermal/demographic period” and “2026 OSM candidate proxy” in the
abstract, Methods, captions and data availability. Do not claim seasonal
representativeness, annual mean, temporal trend, 2024 public access or 2026 heat.

**Confidence.** High; the evidence is explicit and consistent.

**Consequences.** The paper can study how a 2024 thermal/demographic pattern
combines with a 2026 candidate-access network, but not how access changed over
time. Human approval required because this defines the claim scope.

---

## D2 — Historical OSM and temporal stability

**Evidence.** Six historical OSM requests failed (HTTP 406); the historical
pilot file records failures; no comparable snapshot exists. The manuscript
explicitly says no temporal stability claim.

**Alternatives.**
1. Accept claim withdrawal (recommended).
2. Reopen only if a historical archive is recovered; then compare snapshots.
3. Use a current-only proxy with a stronger limitation (essentially option 1).

**Recommendation.** Accept **claim withdrawal**, not “evidence of stability”.
Do not say the 2026 network is representative of 2024. If a reviewer asks
whether the results would change with a 2024 network, the answer is: unknown.

**Confidence.** High.

**Consequences.** The paper cannot support a temporal or historical-access
claim; this is already disclosed. Human approval required.

---

## D3 — Null versus zero support semantics

**Evidence.** 19 original age-no-support cells: 13 recovered, 6 remain null
(`JKT_R003_C031`, `JKT_R057_C063`, `JKT_R061_C009`, `JKT_R061_C010`,
`JKT_R061_C011`, `JKT_R062_C043`). Raw zeros are preserved in `*_raw` columns.
`JKT_R050_C061` is a supported near-zero estimate (population ≈0.00012), not a
no-support cell. No negative values.

**Alternatives.**
1. Accept null for no source support; do not impute (recommended).
2. Impute the six cells from neighbouring grids (not supported by source
   evidence; would fabricate data).
3. Exclude all six from all models (already effectively done for M4; M1–M3
   can retain them for heat/vegetation).

**Recommendation.** Accept the **null/no-source** semantics and preserve raw
zeros. Do not treat unsupported cells as estimated zero population. Report the
six cells, including the two large North Jakarta cells, as a disclosure item.

**Confidence.** High; technical evidence is consistent across the audit.

**Consequences.** M4 common set is 2,536, not 2,538. Human approval is formal
rather than scientific; the technical interpretation is clear.

---

## D4 — M4 construct, weights and interpretation

**Evidence.**
- M4 = 0.30 LST + 0.20 vegetation deficit + 0.25 age count + 0.25 park deficit.
- Weights provisional, fixed before real LST data, not literature-derived,
  unsigned.
- Age count vs total population Spearman 0.999479; count swap Jaccard 0.976654;
  share swap 0.347480; top-M4 vulnerable share 0.2894–0.3016.
- Park Shapley 85.461%; reweighting 13.249%; age 1.289%.
- M4 cutoff 0.873739849 > max near-park 0.869648776; 0/537 near-park cells in
  top 254; top minimum 638.2 m; 174/254 at cap.
- Park-only Jaccard 0.028340; heat-only 0.384196; equal-weight 0.867647.
- Scenario envelope: park threshold 0.521–0.682; weights 0.868–0.954;
  normalisation 0.734–0.814; joint factorial 0.583–0.728.

**Interpretation.** M4 is a composite screening index whose age term is
effectively a population count and whose park term mechanically determines the
top decile under observed inputs. It is not a validated vulnerability index,
not an age-composition model, and not a health-risk model.

**Alternatives.**

| Option | Advantages | Limitations | Required analyses | Manuscript changes | Risk |
|---|---|---|---|---|---|
| **A. Retain + relabel** | Preserves all results; honest; minimal reanalysis; matches evidence | Still arbitrary weights; age redundancy; park dominance | Correct Table 7; add near-park table/figure; restate claims | Rename M4; remove age-vulnerability/park-inequality implications; foreground cutoff | Medium |
| **B. Separate objectives** | Scientifically cleanest; explicit estimands | New models, rankings, sensitivity; major rewrite | M4a heat+population; M4b age share; M4c park access; re-run comparisons | New paper structure and results | Low scientific risk, high production cost |
| **C. Revise M4** | Could reduce mechanical dominance | Arbitrary without theory; loses RC1 comparability; new artifact may be equally arbitrary | Full reanalysis and re-audit | Major rewrite | High |

**Recommendation.** **Option A for this manuscript**, with mandatory
conditions: (i) split/correct Table 7; (ii) remove every age-vulnerability or
park-inequality implication; (iii) display near-park hot cells; (iv) state that
the 85.46% is a descriptive share of model-change rank movement. **Option B** is
the preferred next study. **Option C** is not recommended for the current
preprint.

**Confidence.** High that A is the minimum defensible path; medium that A is
sufficient for a strong paper (B is stronger).

**Consequences.** Without a signed D4, the manuscript cannot claim “spatial
priorities” as a validated applied result. It can claim a transparent screening
audit. Human approval required.

---

## D5 — Count versus composition

**Evidence.** Count swap Jaccard 0.976654 (251/254); vulnerable-share 0.347480
(131/254); child-share 0.451429; elderly-share 0.391781; vulnerable share mean
0.2955, SD 0.0073; vulnerable share vs LST Spearman 0.0057.

**Alternatives.**
1. Count-based exposure as primary; share as separate objective (recommended).
2. Share-based composition as primary (requires a different model and
   denominator policy).
3. Mix count and share in one composite (not recommended; estimand ambiguity).

**Recommendation.** Define the primary estimand as **where many vulnerable
people live (count-based exposure)**. Report the share models as separate
objectives. Never call the count “age vulnerability” or “age composition”.
If the research question is “is age composition associated with heat?”, use a
share model with a population control.

**Confidence.** High.

**Consequences.** M4 remains an exposure-oriented index; the paper cannot claim
to identify age-vulnerable neighbourhoods. Human approval required.

---

## D6 — Hybrid versus fractional population aggregation

**Evidence.** 383 partial cells; 65 <10% coverage; hybrid vs fractional changes
16 top-M4 cells; fractional Jaccard 0.881481; hybrid is not additive under
repartitioning; fractional conservation <4.7e-5 persons. Primary allocation is
unsigned.

**Alternatives.**
1. Retain hybrid for continuity; report fractional as sensitivity (current).
2. Use fractional as primary for additive count accounting (recommended if the
   estimand is total persons per grid).
3. Report both as co-primary; do not choose (acceptable but complicates the
   narrative).

**Recommendation.** For an additive population-exposure estimand, **fractional
allocation is conceptually preferable**. For this manuscript, either (a) switch
primary to fractional and rerun the affected tables/figures, or (b) retain hybrid
but state prominently that it is not additive and report the 16-cell fractional
swap. Do not claim the hybrid is a conserved allocation.

**Confidence.** Medium-high; the arithmetic is clear, the choice is scientific.

**Consequences.** If hybrid remains primary, the paper must not treat population
totals as exactly conserved. Human approval required.

---

## D7 — Thermal support threshold 0.50

**Evidence.** `JKT_R037_C062` has 27.759% valid LST area (6,724.1/24,223.1 m²);
values retained; 0.50/0.25/strict scenarios yield 2,765/2,764/2,752 grids. No
threshold is empirically validated.

**Alternatives.**
1. Retain 0.50 as provisional primary with 0.25/strict sensitivity (recommended).
2. Use 0.25 as primary (restores one cell; less support).
3. Use strict QA (removes 13 additional cells; not necessarily better).
4. Include all measured values with flags (loses a QA rule).

**Recommendation.** Retain **0.50 provisional** and report 0.25/strict as
sensitivity. Do not call the threshold validated. Do not interpret low-support
cells as “no heat”.

**Confidence.** Medium; no empirical basis for a single threshold.

**Consequences.** One cell is excluded from all models; M1/M2 eligibility 2,764.
Human approval required.

---

## D8 — Candidate park access and route assumptions

**Evidence.** 1,015 candidates; 980 unknown, 28 conditional, 7 positive-tag;
0 verified public access; 0 verified entrances; 1,015 unresolved. Baseline 226
missing routes; conservative 407; 167 origin + 78 park connector conflicts;
24,370 directed edges removed. Positive-tag-only stress: 10 destinations,
Jaccard 0.420. Conservative fixed-set Jaccard 0.896. OSM 2026 vs 2024.

**Alternatives.**
1. Candidate proxy only; no public/legal claim (recommended).
2. Field-verify access/entrances for top-impact parks (needed for a stronger
   claim).
3. Treat positive OSM tags as access (not acceptable without verification).
4. Treat missing routes as zero distance (not acceptable).

**Recommendation.** Accept **candidate proxy only**. Baseline routes are
modelled and unvalidated. Report positive-tag and conservative scenarios as
stress tests, not ground truth. No claim of public access, legal route, entrance
or cooling refuge.

**Confidence.** High.

**Consequences.** The park term is an access proxy; policy interpretation must
be limited to screening and field verification. Human approval required.

---

## D9 — Common comparison set 2,536 and selection

**Evidence.** 2,765 master; 229 excluded (222 route-only, 4 route+pop+age,
2 pop-only, 1 low LST); 8.28% grids, 4.22% population; excluded cooler
(40.283 vs 41.486 °C), greener (0.365 vs 0.315), more peripheral (snap 98.81 vs
49.98 m); 18/277 full-thermal M1 top lost; 13 route-missing cells could enter
top 254.

**Alternatives.**
1. Common set for model comparison; report full-area/excluded (recommended).
2. Full-area imputation for missing routes (not supported without a model).
3. Restrict all claims to the common set (honest but loses the full-area
   context).

**Recommendation.** Use the **common set for model comparison**; report the
full-area and excluded cells alongside every priority map; never claim
Jakarta-wide. State that the common set is a conditional estimand.

**Confidence.** High.

**Consequences.** The paper’s inference is conditional; this is already mostly
disclosed. Human approval required for the final selection policy.

---

## D10 — LISA primary convention

**Evidence.** Directed/999/BH 663; two-sided/999/BH 496; directed/9,999/BH 687;
two-sided/9,999/BH 493; directed/999/BY 0; directed/9,999/BY 284;
two-sided/9,999/BY 234. Independent recomputation exact. 999 minimum p=0.001;
9,999 minimum p=0.0001. BY/999 zero is a resolution artifact.

**Alternatives.**

| Convention | Advantages | Limitations | Role |
|---|---|---|---|
| Directed/999/BH | RC1 continuity; fast; one-sided clustering | Coarse p resolution; labels change with permutations | Secondary/continuity |
| **Directed/9,999/BH** | Better resolution; one-sided clustering; stable labels | More compute; still not causal | **Recommended primary** |
| Two-sided/9,999/BH | Detects both tails; conservative | Different label set; less aligned with positive-clustering hypothesis | Sensitivity |
| Directed/9,999/BY | Controls arbitrary dependence | Very conservative; fewer clusters | Sensitivity |
| BY/999 | — | Zero due resolution; not interpretable as “no clustering” | Do not use as primary |

**Recommendation.** Pre-specify **directed/9,999/BH** as primary for each model
map; report directed/999/BH as continuity, two-sided/9,999/BH and BY/9,999 as
sensitivity. Use the full range in the abstract/discussion. Do not select a
convention because it yields more significant cells; select it for the stated
positive-autocorrelation hypothesis and Monte Carlo resolution.

**Confidence.** Medium-high; 999/BH is defensible for exploratory screening but
weaker for confirmatory local claims.

**Consequences.** The M4 significant count becomes 687 (primary) rather than
663; the paper must report both and avoid a single “cluster” narrative. Human
approval required.

---

## D11 — Dynamic World categorical deferral

**Evidence.** Dynamic World probabilities available for 2,764 cells; categorical
labels/fractions absent; probabilities are not fractions; R3 fields null;
deferral proposed but unsigned.

**Alternatives.**
1. Sign a supplementary deferral; no categorical claim (recommended).
2. Obtain a categorical label export and compute fractions (requires GEE run).
3. Use probabilities as if they were fractions (not acceptable).

**Recommendation.** Sign the **deferral**; state that M1–M4 use LST/NDVI only
and that no tree/grass/built-area claim is made. If categorical analysis is
required, obtain a label export and validate denominators.

**Confidence.** High.

**Consequences.** No categorical land-cover claim; the paper remains an
LST/NDVI study. Human approval required for the signed deferral.

---

## D12 — Novelty and claim scope

**Evidence.** Closest prior work: Sidiqui et al. (2022, Geelong), Kim & Kwak
(2026, older-adult park access), Fung et al. (2024, social vulnerability
prioritisation), Sobhaninia et al. (2025, siting review), Rizki et al. (2024,
East Jakarta), Varquez et al. (2020, Jakarta elderly mortality). Combination-only
novelty fails. The manuscript’s contribution is the attribution/uncertainty
audit and negative findings.

**Alternatives.**
1. Claim attribution/uncertainty audit + negative findings (recommended).
2. Claim a new integrated framework (not supported).
3. Claim a validated vulnerability map (not supported).
4. Claim a new accessibility method (not supported; the park term is simple).

**Recommendation.** Claim **methodological/empirical attribution and uncertainty
audit**, with explicit negative findings. No “first”, “novel combination”,
“validated”, “superior” or causal language. Make the literature matrix and the
Sidiqui/Geelong context explicit.

**Confidence.** High that the narrower claim is defensible; conditional on the
targeted (not systematic) review.

**Consequences.** The paper is positioned as a screening/audit study, not a new
framework. Human approval required.

---

## D13 — Final scientific release

**Recommendation:** **HOLD**. The Table 7 defect is material; D4, D10 and RS-01
are unsigned; park access and selection claims are conditional; author
contributions/funding/conflicts are placeholders. Do not mark D13 approved.

**Conditions for moving to CONDITIONAL PASS:**
1. Correct/split Table 7 and the surrounding text.
2. Sign D4 (Option A minimum) and remove residual age/park implications.
3. Pre-specify D10 and report the full range.
4. Sign RS-01 claim restriction or recover lineage.
5. Confirm D1/D2/D5/D6/D7/D8/D9/D11/D12.
6. Update data/code availability (RC1 vs RC2) and reference details.
7. Final independent re-audit of the revised manuscript.
8. Human approval of authors, contributions, funding, conflicts and licence.

---

## Cross-cutting note on evidence versus inference

- The arithmetic (scores, ranks, Jaccard, Shapley, cutoff, LISA counts) is
  **evidence** and is independently verified.
- The interpretation that M4 is a “screening index” is an **inference** from the
  construct; it is defensible but requires the D4 label.
- The recommendation to retain/relabel M4 (Option A) is a **recommendation**, not
  a scientific fact; the coordinator must decide.
- The recommendation of directed/9,999/BH is a **statistical judgement**, not a
  uniquely correct convention; it must be pre-specified and reported with
  alternatives.
