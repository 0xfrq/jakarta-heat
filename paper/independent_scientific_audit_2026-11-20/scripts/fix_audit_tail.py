from pathlib import Path
p = Path(r"D:\jakarta-heat-paper\paper\independent_scientific_audit_2026-11-20\INDEPENDENT_SCIENTIFIC_AUDIT.md")
s = p.read_text(encoding="utf-8")
idx = s.find("## 10. Claim status")
assert idx > 0
prefix = s[:idx]
tail = """## 10. Claim status

The updated `CLAIM_EVIDENCE_MATRIX.csv` has 39 claims (36 VERIFIED,
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
"""
p.write_text(prefix + tail, encoding="utf-8")
print("rewrote", len(prefix + tail))
