from pathlib import Path
p = Path(r"D:\jakarta-heat-paper\paper\zenodo_preprint\FINAL_PREPRINT_RELEASE_RECORD.md")
lines = p.read_text(encoding="utf-8").splitlines()
for i, line in enumerate(lines):
    if "AWAITING MANUAL UPLOAD" in line:
        if line.startswith("**Status:**"):
            lines[i] = "**Status:** `ZENODO PACKAGE READY — FINAL LITERATURE REVISION COMPLETE`"
        else:
            lines[i] = "`ZENODO PACKAGE READY — FINAL LITERATURE REVISION COMPLETE`"
p.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("status updated")
