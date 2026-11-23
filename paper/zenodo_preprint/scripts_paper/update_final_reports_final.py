from pathlib import Path
p = Path(r"D:\jakarta-heat-paper\paper\independent_scientific_audit_2026-11-20\FINAL_NUMERICAL_CONSISTENCY_CHECK.md")
s = p.read_text(encoding="utf-8")
s = s.replace("""- Submission candidate: **23 pages**; no banner, neutral footer, no undefined
  citations/references.
- Internal review: **23 pages**; concise internal identifier only.
- Supplement: **7 pages**; S1—S9, including 49 scenarios, six no-support cells,
  eligibility reconciliation and primary LISA table.""", """- Submission candidate: **24 pages**; no banner, neutral footer, no undefined
  citations/references; declarations, AI disclosure and CC BY 4.0 statement
  present.
- Internal review: **24 pages**; concise internal identifier only.
- Supplement: **8 pages**; S1—S9, including 49 scenarios, six no-support cells,
  eligibility reconciliation, primary LISA table and declarations.""")
s = s.replace("""| `Manuscript-submission-candidate.pdf` | 23 | 2,416,403 | `66302DA1618D519A39152CAE618981AF4FAB3D30B42EC47E49A6A5AF5E470066` |
| `Manuscript-internal-review.pdf` | 23 | 2,416,668 | `34F84957BE807149DF9BD333A261DEA1902987C92DAC08B6F83878934CC7666D` |
| `Supplementary-submission-candidate.pdf` | 7 | 799,191 | `1CD6992723632236D61F4E0A85EA054268E373EFEE02A3B6277843ABB82A2675` |""", """| `Manuscript-submission-candidate.pdf` | 24 | 2,418,475 | `92BA6A2B57467F952D4A07A1A954B35AA68198F0CA1D10C286015AB8D61F3F31` |
| `Manuscript-internal-review.pdf` | 24 | 2,418,729 | `F8043E882A4C224F56F2D682AC1DF6141CB7C7571707049071EB2EA4A986592C` |
| `Supplementary-submission-candidate.pdf` | 8 | 801,426 | `9CD990B91FDC94DAD04D5CE5663D42CD80920C8E9ECEC8908387133ACE096A58` |""")
p.write_text(s, encoding="utf-8")

p2 = Path(r"D:\jakarta-heat-paper\paper\independent_scientific_audit_2026-11-20\FINAL_EDITORIAL_REPORT.md")
s2 = p2.read_text(encoding="utf-8")
s2 = s2.replace("""warnings. The clean candidate is 23 pages; the internal review is 23 pages; the
supplement is 7 pages. The title page, attribution tables, LISA figure/table,
references and supplement pages were rendered and inspected. No undefined
citations or references remain.""", """warnings. The clean candidate is 24 pages; the internal review is 24 pages; the
supplement is 8 pages. The title page, declarations, attribution tables, LISA
figure/table, references and supplement pages were rendered and inspected. No
undefined citations or references remain. The public PDF contains Author
Contributions, Funding, Conflicts of Interest, Data and Code Availability,
AI-assisted tools disclosure, the CC BY 4.0 statement, and the template
attribution.""")
p2.write_text(s2, encoding="utf-8")
print("final reports updated")
