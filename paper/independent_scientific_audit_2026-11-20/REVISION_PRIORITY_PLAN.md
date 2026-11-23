# Revision Priority Plan

**Audit date:** 20 November 2026
**Manuscript status:** HOLD
**Purpose:** ordered, dependency-aware revision plan; no manuscript changes were
made by this audit.

---

## 1. Priority definitions

- **P0 — release-blocking scientific error or missing approval.** Must be fixed
  before any public preprint.
- **P1 — major scientific/interpretive issue.** Must be fixed before a credible
  preprint or explicitly signed as a limitation.
- **P2 — quality/reproducibility/consistency issue.** Fix before submission if
  feasible.

---

## 2. P0 — release-blocking

### P0-1. Correct and split Table 7

**Status: DONE in the current manuscript revision.** Table 7 is now M3-relative
and Table 8 is M4-relative; the Jaccard/retention wording is corrected.

**Problem.** The table caption/footnote state that all Jaccard values are
M4-relative, but the reweighting/age/park rows are M3-relative. Exact
M4-relative values differ materially (park addition 0.861, not 0.490;
reweighting 0.423, not 0.961; age 0.419, not 0.984).

**Actions.**
1. Create Table 7a: incremental effects relative to M3 (M3 reference 1.000;
   reweighting 0.961/249; age 0.984/252; park 0.490/167; combinations; M4
   0.411/148).
2. Create Table 7b: construct/ablation comparisons relative to M4 (M4 reference
   1.000; M3 0.411/148; reweighting 0.423/151; age 0.419/150; park 0.861/235;
   combined; no-park 0.423/151; park-only 0.028/14; heat-only 0.384/141;
   equal-weight 0.868/236; total-count 0.977/251; vulnerable-share 0.347/131;
   child-share 0.451/158; elderly 0.392/143; proportional 0.924/244).
3. Update Section 5.4 text so every number names its baseline.
4. Update `CLAIM_EVIDENCE_MATRIX.csv` (C33/C39), `FIGURE_TABLE_REGISTER.md`, and
   the supplement if it repeats the table.
5. Add a one-sentence explanation of why the two baselines answer different
   questions.

**Owner:** modeling lead + manuscript lead.
**Dependency:** none.
**Acceptance:** no table/caption/text mixing of M3 and M4 baselines; independent
recomputation matches.

### P0-2. Sign D4 (M4 construct) and relabel M4

**Problem.** M4 is not a validated vulnerability index; age count is nearly
collinear with population; park term mechanically excludes near-park cells.
Current table error weakens the relabeling.

**Actions.**
1. Coordinator signs Option A (minimum) or chooses B/C.
2. If A: rename M4 in title/abstract/Methods/Results/Discussion to
   “provisional heat–population–park-deficit screening index”; remove
   age-vulnerability and park-inequality implications.
3. Add a near-park hot-cell table/figure (cutoff, max near-park score,
   `JKT_R056_C048`, 236/254 cooler).
4. State that 85.46% is a descriptive share of model-change rank movement.
5. Remove any “M4 improves/validates” language.

**Owner:** PI/coordinator + modeling lead.
**Dependency:** P0-1 (table must be correct before relabeling text).
**Acceptance:** all M4 claims match the screening construct; no age/park
overclaim.

### P0-3. Sign D10 (LISA convention)

**Problem.** Directed/999/BH is provisional; 0–687 significant cells; BY/999
zero is a resolution artifact.

**Actions.**
1. Pre-specify primary: recommended directed/9,999/BH.
2. Report directed/999/BH as continuity, two-sided/9,999/BH and BY/9,999 as
   sensitivity.
3. Update abstract/results/discussion/table to report the full range.
4. Recompute primary labels for M1–M4 if the primary changes.
5. Never use BY/999 zero as evidence of no clustering.

**Owner:** spatial/statistical lead + coordinator.
**Dependency:** none, but must precede final results text.
**Acceptance:** primary convention pre-specified; all counts and labels
reproducible; no confirmatory overclaim.

### P0-4. Sign RS-01 claim restriction or recover lineage

**Problem.** Scene manifest 0 rows; task/AOI null; GeoTIFF tags empty; 2024 is
declared, not verified.

**Actions.**
1. Attempt recovery of scene IDs/dates/task/AOI (authorized operator).
2. If unavailable, sign a written restriction: 2024 = declared recipe period;
   no annual/seasonal/trend/air-temperature/personal-exposure claim.
3. Use “declared 2024 thermal period” consistently in abstract, Methods, Figure
   1, data availability.
4. Do not say “verified 2024 data.”

**Owner:** remote-sensing lead + coordinator.
**Dependency:** none.
**Acceptance:** signed restriction or recovered lineage; all manuscript
references consistent.

### P0-5. Resolve D1/D2/D5/D6/D7/D8/D9/D11/D12

**Problem.** Scientific decisions remain unsigned; manuscript claims depend on
them.

**Actions.** Use `SCIENTIFIC_DECISION_RECOMMENDATIONS.md`; obtain signatures or
explicit provisional labels. Prioritize D5 (count vs share), D6 (aggregation),
D8 (park access), D9 (common set).

**Owner:** coordinator.
**Dependency:** P0-1/P0-2/P0-3/P0-4 for coherent text.
**Acceptance:** decision register signed; manuscript claims match.

---

## 3. P1 — major scientific/interpretive

### P1-1. Normalize data/code availability (RC1 vs RC2)

**Problem.** Manuscript reports RC1 clean-checkout failure; RC2 fixes it.
Readers may not know which artifact is authoritative.

**Actions.**
1. State RC1 is the frozen numerical reference.
2. If RC2 is adopted for reproducibility, verify implementation/output identity
   and cite RC2 receipt; do not change numbers.
3. Update the software-portability limitation accordingly.
4. Do not claim RC2 scientific approval.

**Owner:** integration lead + manuscript lead.
**Dependency:** P0 decisions (do not mix).
**Acceptance:** one clear artifact story; no contradictory test claims.

### P1-2. Sharpen novelty and literature positioning

**Problem.** Combination-only novelty fails; contribution is incremental.

**Actions.**
1. State the attribution/uncertainty/negative-findings contribution in one
   precise paragraph.
2. Add “Greater Geelong, Australia” to the Sidiqui row.
3. Cite Vargas Molina et al. (2026) in the climate-shelter/access paragraph or
   remove it from the reference database/matrix.
4. Reconcile 62 BibTeX entries vs 61 cited references.
5. Avoid “first”, “novel framework”, “validated”.

**Owner:** PI + literature lead.
**Dependency:** none.
**Acceptance:** novelty statement survives a skeptical reviewer; reference
counts consistent.

### P1-3. Strengthen selection/generalization disclosure

**Problem.** 229 excluded cells; 18/277 full-thermal top lost; 13 possible top
cells; common set not Jakarta-wide.

**Actions.**
1. Show excluded cells in every priority map (already mostly done).
2. Report full-area vs common-set counts.
3. Keep “five mainland cities under the common-set configuration” language.
4. Add the 13-cell bound to the abstract or limitations (already in limitations).

**Owner:** modeling lead.
**Dependency:** P0-1.
**Acceptance:** no Jakarta-wide phrase; selection bounds visible.

### P1-4. Park-access claim discipline

**Problem.** 0 verified access/entrances; 226/407 missing; positive-tag stress
0.420; OSM 2026 vs 2024.

**Actions.**
1. Keep candidate-proxy wording in all tables/captions.
2. Add positive-tag and conservative stress results to main text/table.
3. State field verification is required before policy use.
4. No “public park access” claim.

**Owner:** GIS lead.
**Dependency:** P0-2.
**Acceptance:** no access overclaim; stress range reported.

### P1-5. Add near-park hot-cell disclosure to main text

**Problem.** The mechanical cutoff is disclosed, but a reader may miss the
near-park hot cells.

**Actions.**
1. Add a small table or figure panel with the 537 near-park cells:
   cutoff, max score, 0/537, min distance, example cell, 236/254 cooler.
2. Put it in Results 5.7, not only supplement.

**Owner:** modeling lead.
**Dependency:** P0-1.
**Acceptance:** disclosure visible in main text.

---

## 4. P2 — quality and consistency

### P2-1. Reference formatting

- Brace proper nouns: `OpenStreetMap`, `Jakarta`, `R2025A`, etc.
- Fix duplicate `Siswanto Siswanto` formatting if desired.
- Add missing middle initials (Voelkel, etc.) if desired.
- Ensure reference list has 61 cited entries.

### P2-2. Mathematical precision

- Define \(\log\) as natural logarithm.
- State that park deficit is not renormalized after capping (already in Methods).
- State that rank tie-break uses unclipped score (already in Methods; keep).

### P2-3. Table/figure captions

- Add exact denominators and baseline labels.
- Ensure all maps show excluded cells.
- Keep “under observed inputs” qualifier on cutoff claims.

### P2-4. Abstract length/readability

- Consider a 250–300 word abstract; keep all key qualifications.

### P2-5. Supplement consistency

- Add the corrected Table 7 split if the supplement repeats any attribution
  values.
- Add provenance note for the independent audit? Optional.

---

## 5. Dependency graph

```text
P0-1 Table 7 fix
  ├── P0-2 M4 relabel
  │     ├── P1-4 park-access discipline
  │     └── P1-5 near-park disclosure
  ├── P1-3 selection disclosure
  └── P2-3 captions

P0-3 LISA primary
  └── P0-5 decision signatures

P0-4 RS-01 restriction
  └── P0-5 decision signatures

P1-1 RC1/RC2 artifact story
  └── P0-5 decision signatures

P1-2 literature/novelty
  └── P0-5 D12 signature

All P0/P1
  └── final independent re-audit
        └── CONDITIONAL PASS preprint
```

---

## 6. Suggested sequence

1. **Day 1:** P0-1 Table 7 correction; independent check of corrected table.
2. **Day 2:** P0-2 M4 relabel; P1-5 near-park disclosure.
3. **Day 3:** P0-3 LISA primary; recompute/report.
4. **Day 4:** P0-4 RS-01 restriction; P1-1 artifact story.
5. **Day 5:** P0-5 decisions; P1-2 literature; P1-3/P1-4 claim discipline.
6. **Day 6:** P2 consistency; rebuild PDF; visual check.
7. **Day 7:** final independent re-audit; release decision.

---

## 7. Definition of done for CONDITIONAL PASS

- Table 7 split/corrected; no baseline mixing anywhere.
- M4 relabeled; near-park hot cells in main text.
- LISA primary pre-specified; full range reported.
- RS-01 signed restriction or recovered lineage.
- D1–D12 signed or explicitly provisional.
- Park access and selection claims consistent.
- RC1/RC2 artifact story consistent.
- Reference details fixed.
- Author/contributions/funding/conflicts approved.
- Corrected PDF rebuilt and inspected.
- Final independent re-audit completed.
