from pathlib import Path
p = Path(r"D:\jakarta-heat-paper\paper\independent_scientific_audit_2026-11-20\FINAL_RESEARCH_DECISIONS.md")
s = p.read_text(encoding="utf-8")
old = """**Applied:** clean publication candidate prepared, but no upload, submission or
DOI request. Public release still requires author confirmation, contribution
and funding/conflict declarations, licence approval, and human acceptance of the
remaining Landsat provenance limitation."""
new = """**Applied:** clean Zenodo preprint package prepared, but no upload, submission,
publication or DOI request. The coordinator confirmed author metadata,
corresponding author, collective contributions, no external funding, no
competing interests, CC BY 4.0, and acceptance of the restricted Landsat
interpretation. Manual record review and upload remain. No DOI may be claimed
before Zenodo assigns one."""
if old not in s:
    raise SystemExit("D13 text not found")
s = s.replace(old, new, 1)
s = s.replace("| D13 | No public release yet | Applied | Required |", "| D13 | No public release yet; package built | Applied | Manual upload/review |")
p.write_text(s, encoding="utf-8")
print("D13 updated")
