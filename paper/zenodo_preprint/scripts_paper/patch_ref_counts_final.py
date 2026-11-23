from pathlib import Path
p = Path(r"D:\jakarta-heat-paper\paper\independent_scientific_audit_2026-11-20\FINAL_NUMERICAL_CONSISTENCY_CHECK.md")
s = p.read_text(encoding="utf-8")
start = s.find("- Claim C27")
end = s.find("## 11. PDF consistency", start)
if start < 0 or end < 0:
    raise SystemExit("block not found")
new = """- Claim C27 (Landsat scene/task/AOI lineage) remains technically BLOCKED; the
  release record documents editorial acceptance of the restricted preprint
  interpretation without changing that technical status.
- References: **67 cited** from a 67-entry database. Of the 67 cited entries,
  **64 carry DOI metadata** and **3 are no-DOI** items (Oke's 1984 book, the
  OpenStreetMap snapshot, and project documentation). USGS DOI
  `10.5066/P9OGBGM6`; WorldPop DOI `10.5258/SOTON/WP00841`.

"""
s = s[:start] + new + s[end:]
p.write_text(s, encoding="utf-8")

p2 = Path(r"D:\jakarta-heat-paper\paper\independent_scientific_audit_2026-11-20\FINAL_EDITORIAL_REPORT.md")
s2 = p2.read_text(encoding="utf-8")
s2 = s2.replace("The compiled manuscript has 61 cited references.", "The compiled manuscript has 67 cited references.")
p2.write_text(s2, encoding="utf-8")

p3 = Path(r"D:\jakarta-heat-paper\paper\zenodo_preprint\FINAL_PREPRINT_RELEASE_RECORD.md")
s3 = p3.read_text(encoding="utf-8")
s3 = s3.replace("Bibliography: 61 cited references; no undefined citations/references.", "Bibliography: 67 cited references; no undefined citations/references.")
p3.write_text(s3, encoding="utf-8")
print("counts patched")
