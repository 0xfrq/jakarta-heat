from pathlib import Path
p = Path(r"D:\jakarta-heat-paper\paper\independent_scientific_audit_2026-11-20\FINAL_NUMERICAL_CONSISTENCY_CHECK.md")
s = p.read_text(encoding="utf-8")
s = s.replace("- Submission candidate: **24 pages**; no banner, neutral footer, no undefined", "- Submission candidate: **25 pages**; no banner, neutral footer, no undefined")
s = s.replace("- Internal review: **24 pages**; concise internal identifier only.", "- Internal review: **25 pages**; concise internal identifier only.")
s = s.replace("| `Manuscript-submission-candidate.pdf` | 24 | 2,418,475 | `92BA6A2B57467F952D4A07A1A954B35AA68198F0CA1D10C286015AB8D61F3F31` |", "| `Manuscript-submission-candidate.pdf` | 25 | 2,426,183 | `72E4E50B60716408D3AE60A66DA1D422BD1A19E42D62F3D0A72660EB7553A986` |")
s = s.replace("| `Manuscript-internal-review.pdf` | 24 | 2,418,729 | `F8043E882A4C224F56F2D682AC1DF6141CB7C7571707049071EB2EA4A986592C` |", "| `Manuscript-internal-review.pdf` | 25 | 2,426,719 | `234BC4F7780D49A73844E4390B3E5FF04BFBB6B4C7876E2C6EDF2B1EBA0AB47B` |")
p.write_text(s, encoding="utf-8")

p2 = Path(r"D:\jakarta-heat-paper\paper\independent_scientific_audit_2026-11-20\FINAL_EDITORIAL_REPORT.md")
s2 = p2.read_text(encoding="utf-8")
s2 = s2.replace("warnings. The clean candidate is 24 pages; the internal review is 24 pages; the\nsupplement is 8 pages.", "warnings. The clean candidate is 25 pages; the internal review is 25 pages; the\nsupplement is 8 pages.")
p2.write_text(s2, encoding="utf-8")
print("final reports pages updated")
