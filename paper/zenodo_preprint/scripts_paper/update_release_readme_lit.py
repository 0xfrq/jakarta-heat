from pathlib import Path
p = Path(r"D:\jakarta-heat-paper\paper\zenodo_preprint\zenodo_release\RELEASE_README.md")
s = p.read_text(encoding="utf-8")
s = s.replace("**Status:** package ready for manual review and upload. No Zenodo record has\nbeen created and no DOI has been reserved.", "**Status:** `ZENODO PACKAGE READY — FINAL LITERATURE REVISION COMPLETE`. The\npackage is ready for manual review and upload; no Zenodo record or DOI has been\ncreated.")
needle = "## Package contents"
note = """## Literature revision

This version includes the final related-work revision: Perdinan et al. (2026),
Fitria et al. (2026), Ramadhanis et al. (2026), Dong et al. (2024), Elmarakby
and Elkadi (2024), and Ulfiasari and Yola (2022). The manuscript now has 67
cited references and a focused eight-row literature comparison. The empirical
results are unchanged.

"""
if "## Literature revision" not in s:
    s = s.replace(needle, note + needle, 1)
s = s.replace("**ZENODO PACKAGE READY — AWAITING MANUAL UPLOAD**", "**ZENODO PACKAGE READY — FINAL LITERATURE REVISION COMPLETE**")
s = s.replace("**ZENODO PACKAGE READY - AWAITING MANUAL UPLOAD**", "**ZENODO PACKAGE READY — FINAL LITERATURE REVISION COMPLETE**")
p.write_text(s, encoding="utf-8")
print("release readme updated")
