from pathlib import Path
p = Path(r"D:\jakarta-heat-paper\paper\zenodo_preprint\FINAL_PREPRINT_RELEASE_RECORD.md")
s = p.read_text(encoding="utf-8")
s = s.replace("**Status:** `ZENODO PACKAGE READY - AWAITING MANUAL UPLOAD`", "**Status:** `ZENODO PACKAGE READY - FINAL LITERATURE REVISION COMPLETE`")
s = s.replace("| `Jakarta_Heat_Priorities_Preprint_v1.pdf` | 24 | 2,418,475 | `92ba6a2b57467f952d4a07a1a954b35aa68198f0ca1d10c286015ab8d61f3f31` |", "| `Jakarta_Heat_Priorities_Preprint_v1.pdf` | 25 | 2,426,183 | `72e4e50b60716408d3ae60a66da1d422bd1a19e42d62f3d0a72660eb7553a986` |")
s = s.replace("- Main PDF: 24 pages; neutral footer; no draft banner; no Zenodo deposit claim.", "- Main PDF: 25 pages; neutral footer; no draft banner; no Zenodo deposit claim.")
s = s.replace("`ZENODO PACKAGE READY - AWAITING MANUAL UPLOAD`", "`ZENODO PACKAGE READY - FINAL LITERATURE REVISION COMPLETE`")
# Add a concise literature revision note before the current status section.
needle = "## 8. Current status"
note = """## 7b. Final literature revision

The final related-work revision added Perdinan et al. (2026), Fitria et al.
(2026), Ramadhanis et al. (2026), Dong et al. (2024), Elmarakby and Elkadi
(2024), and Ulfiasari and Yola (2022). Table 1 was reduced to eight focused
rows. The compiled manuscript now has **67 cited references** and no undefined
citations. No empirical output was changed. The supporting comparison and
novelty reviews are in
`paper/independent_scientific_audit_2026-11-20/FINAL_LITERATURE_COMPARISON.md`
and `NOVELTY_POSITIONING_REVIEW.md`.

"""
if needle in s and "## 7b. Final literature revision" not in s:
    s = s.replace(needle, note + needle, 1)
p.write_text(s, encoding="utf-8")
print("release record updated")
