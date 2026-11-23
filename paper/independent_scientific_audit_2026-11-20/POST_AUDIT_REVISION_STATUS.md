# Post-Audit Revision Status

**Date:** 21 November 2026
**Scope:** manuscript corrections applied after the independent audit, using
RC2 engineering evidence and reference verification.
**Current manuscript status:** `COMPLETE DRAFT / PENDING SCIENTIFIC APPROVAL`
**Current release recommendation:** **HOLD** for human scientific approval;
the Table 7 defect and Jaccard wording are resolved.

---

## 1. Corrections applied

| Item | Before | After |
|---|---|---|
| Jaccard wording | Abstract/Results/Conclusion described 141/254 as “38.4% overlap” | Now states 141/254 = **55.5% retention**, Jaccard 0.384 (shared/union 367); Table 6 note adds all pairwise shared/retention counts |
| Attribution table | One table mixed M3-relative and M4-relative Jaccard while saying reference M4 | Split into **Table 7** (incremental, M3 baseline) and **Table 8** (construct/ablation, M4 baseline); text, captions, footnotes and claim register corrected |
| RC1 software limitation | Said clean checkout had one failure and three receipt mismatches | Now reports RC2 remediation: clean-checkout 236 tests + 7 subtests, 0 failures/errors/skips; receipts 9/9; manifests 69/69 and 80/80; replay max diff 0.0; results remain RC1 |
| USGS reference | Product-guide URL with year 2024 | Dataset DOI `10.5066/P9OGBGM6`, EROS Center, year 2020, Landsat 8–9 OLI/TIRS Level-2 Collection 2 |
| Author marker | `\Letter` glyph appeared as a stray superscript next to first author | Removed; correspondence line lists all three e-mails |
| Zenodo footer | Could imply deposit/acceptance | Banner explicitly states the footer profile is a presentation format only |
| Supplement | S1–S6 only; no full scenario/demographic/eligibility data | S6 all 49 executed scenarios; S7 six no-support cells; S8 eligibility reconciliation; S9 provenance; machine-readable CSVs added |
| Claim register | C39 BLOCKED | C39 now VERIFIED: Table 7/8 split confirmed. Register: 39 VERIFIED, 2 PROVISIONAL, 1 BLOCKED (RS-01) |

## 2. Still HOLD

The following are **not** resolved by the corrections:

- **D4 M4 construct** — still provisional/unsigned. The manuscript labels M4 as
  a screening index; human approval is still required.
- **D10 LISA convention** — still provisional. The manuscript reports the range;
  the primary convention is not signed.
- **RS-01 Landsat lineage** — still BLOCKED. The manuscript uses “declared 2024”;
  a signed claim restriction or recovered lineage is required.
- **D1, D2, D5–D9, D11, D12** — recommendations exist; signatures do not.
- **Park access/entrances** — still candidate proxy, 0 verified.
- **Common subset/selection** — conditional; no Jakarta-wide claim.
- **Author contributions, funding, conflicts, corresponding author, licence** —
  human approval required.
- **Final independent re-audit** — not yet performed on the corrected
  manuscript.

## 3. Current readiness

- **Table 7 defect:** resolved.
- **Jaccard interpretation:** resolved.
- **RC2 engineering evidence:** integrated as engineering context only.
- **References:** 61 cited entries verified; USGS corrected; minor
  bibliographic polish remains (Vargas citation/removal, Sidiqui location,
  capitalization).
- **PDF:** rebuild required after the corrections; see
  `paper/zenodo_preprint/COMPILATION_REPORT.md`.
- **Release:** **HOLD** until human scientific approval and final re-audit.

## 4. What the coordinator must decide

1. Sign D4 (Option A retain/relabel, or choose B/C).
2. Sign D10 (recommended directed/9,999/BH primary).
3. Sign RS-01 claim restriction or recover lineage.
4. Sign D1/D2/D5–D9/D11/D12.
5. Approve author contributions, corresponding author, funding, conflicts and
   licence.
6. Authorize a final independent re-audit and, only afterward, a preprint
   deposit.
