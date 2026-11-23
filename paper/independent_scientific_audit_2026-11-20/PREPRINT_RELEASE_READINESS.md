# Preprint Release Readiness

**Assessment date:** 20 November 2026
**Manuscript:** *From Thermal Hotspots to Spatial Priorities: Attribution and
Sensitivity of Urban Heat Screening in Jakarta*
**Frozen reference:** RC1 `3b8ed05be92c35bbb2b3a617688540ee856b11c8`
**Decision:** **HOLD**
**Not:** PASS, CONDITIONAL PASS, READY FOR PUBLICATION

---

## 1. Decision

The manuscript must **not** be uploaded to Zenodo or otherwise publicly released
in its current form.

Reasons, in order of severity:

1. **M4 construct remains unsigned (D4).** The paper labels it as a screening
   index, but the age count is effectively population and the park term
   mechanically determines the top decile. A signed construct decision is
   required.
2. **LISA primary convention remains unsigned (D10).** Directed/999/BH is
   provisional; the significant-cell count ranges from 0 to 687 across
   conventions. A pre-specified primary is required.
3. **RS-01 is BLOCKED.** No scene IDs, acquisition dates, task IDs or AOI hash.
   The 2024 label is a declared recipe period; a signed restriction is required.
4. **Park access and selection claims remain conditional.** 0 verified public
   access/entrances; 229 excluded cells; common set not Jakarta-wide.
5. **Human approvals are missing.** Author contributions, funding, conflicts,
   corresponding author, licence and D1–D12 are not signed.
6. **Final independent re-audit has not been performed on the corrected,
   rebuilt PDF.**

The Table 7 baseline defect and the Jaccard wording have been **corrected in the
current manuscript revision** (Table 7 M3-relative; Table 8 M4-relative;
141/254 = 55.5% retention, Jaccard 0.384). They are no longer release blockers,
but the corrected PDF still needs final verification.

---

## 2. Gate matrix

| Gate | Status | Evidence | What is needed |
|---|---|---|---|
| Template and LaTeX build | **PASS** | Zenodo 24 pp; neutral 24 pp; supplement 7 pp; no undefined citations | None for build |
| Model arithmetic | **PASS** | Scores max diff 0.0; ranks 0 mismatches; Jaccard/Shapley exact | None |
| Table/text consistency | **PASS (corrected)** | Table 7 M3-relative; Table 8 M4-relative; Jaccard/retention wording corrected | Rebuild/inspect final PDF |
| M4 construct (D4) | **HOLD** | Age count ρ=0.9995; park Shapley 85.46%; 0/537 near-park; mechanical cutoff | Sign Option A (or B/C decision); relabel/rewrite |
| LISA (D10) | **HOLD** | 663/496/687/493/0/284/234; 999 resolution 0.001 | Pre-specify primary; report full range |
| Landsat lineage (RS-01) | **BLOCKED** | Scene manifest 0 rows; task/AOI null; GeoTIFF tags empty | Recover lineage or sign claim restriction |
| Park access | **HOLD** | 0 verified access/entrances; 1,015 unresolved; 226/407 missing | Candidate-proxy wording; field verification for stronger claim |
| Selection/generalisation | **CONDITIONAL** | 229 excluded; 8.28%/4.22%; cooler/greener/peripheral; 13 possible top cells | Report excluded/full-area; no Jakarta-wide |
| Demographic support | **CONDITIONAL** | 6 null cells; 13 recovered; raw zeros preserved | Sign D3; report nulls |
| Aggregation (D6) | **CONDITIONAL** | Hybrid non-additive; fractional J=0.881; 16 top swaps | Sign primary; report both |
| Thermal threshold (D7) | **CONDITIONAL** | 0.50 provisional; JKT_R037_C062 27.759% | Sign threshold with sensitivity |
| Dynamic World (D11) | **CONDITIONAL** | Probabilities 2,764; labels absent | Sign deferral; no categorical claim |
| Novelty (D12) | **CONDITIONAL** | Closest prior work; combination-only fails; attribution audit remains | Sharpen claim; update literature details |
| Software portability | **PASS (engineering)** | RC2: clean-checkout 236 tests + 7 subtests, 0 failures/errors/skips; receipts 9/9; manifests 69/69 and 80/80; replay max diff 0.0 | Keep RC1 empirical results; label RC2 as engineering |
| Author/contributions/funding/conflicts | **HOLD** | Placeholders | Human approval |
| Final independent re-audit | **HOLD** | Not performed on corrected manuscript | Re-audit after revisions |

---

## 3. What can be released now (internal only)

The following statements are defensible for internal discussion, not public
release:

- RC1 is a reproducible exploratory screening artifact for five mainland
  Jakarta cities.
- The common subset contains 2,536 grids; 229 are excluded for documented
  support/route reasons.
- Under the provisional M4, the top decile is dominated by the park-deficit
  term; this is a construct result, not an empirical claim that parks are
  unimportant.
- Age count is nearly collinear with total population; M4 does not estimate age
  composition.
- LISA labels are convention-sensitive; no p=0 claim.
- OSM is 2026; thermal/demography are declared 2024; this is a mixed-period
  proxy.

## 4. What must not be released

- “2024 public park access was verified.”
- “M4 identifies age-vulnerable heat inequality.”
- “All top-priority cells lack parks” as an empirical finding without the
  construct explanation.
- “M4 improves health/policy outcomes.”
- “All priorities are robust.”
- “Jakarta-wide.”
- “p=0” or “significant everywhere.”
- “Edge/browser validation passed.”
- “Peer-reviewed” or “accepted.”
- Any manuscript DOI (none assigned).

---

## 5. Conditions for CONDITIONAL PASS (preprint)

A preprint release could be considered after all of the following:

1. **Verify Table 7/8 split** in the rebuilt PDF: Table 7 is M3-relative and
   Table 8 is M4-relative; no mixed-baseline text remains.
2. **D4 signed**: Option A relabel (minimum) with near-park hot-cell disclosure;
   remove age-vulnerability/park-inequality implications.
3. **D10 signed**: pre-specified primary convention and full sensitivity range.
4. **RS-01 signed**: claim restriction or recovered lineage.
5. **D1/D2/D5/D6/D7/D8/D9/D11/D12 signed** or explicitly marked provisional.
6. **Data/code availability updated**: state RC1 empirical results vs RC2
   engineering; RC2 evidence is already integrated.
7. **Literature details fixed**: Sidiqui/Geelong; Vargas citation or removal;
   reference count; capitalisation.
8. **Author/contributions/funding/conflicts** approved by all authors.
9. **Final independent re-audit** of the corrected manuscript and PDF.
10. **No DOI claimed** until Zenodo assigns one after upload.

## 6. Conditions for READY FOR PUBLICATION

Not achievable in this audit. It would require, in addition to the above:

- external validation or a clear statement that none exists;
- a validated park-access/entrance audit or a permanently restricted claim;
- a health/outcome study if health claims are desired (not part of this paper);
- journal peer review and acceptance;
- final human sign-off on all scientific decisions.

---

## 7. Final recommendation

**HOLD.** The manuscript is a substantive, reproducible, and scientifically
interesting exploratory draft. It is not a validated vulnerability or policy
paper. The Table 7 defect and Jaccard wording are corrected in the current
revision; resolve D4, D10 and RS-01, obtain human approvals, rebuild and inspect
the PDF, then re-audit. A **CONDITIONAL PASS** preprint is achievable.
**READY FOR PUBLICATION** is not supported by the current evidence.
