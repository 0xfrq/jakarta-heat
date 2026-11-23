from pathlib import Path
p = Path(r"D:\jakarta-heat-paper\paper\independent_scientific_audit_2026-11-20\FINAL_EDITORIAL_REPORT.md")
lines = p.read_text(encoding="utf-8").splitlines()
for i, line in enumerate(lines):
    if line.startswith("- First author is proposed as corresponding author"):
        lines[i] = "- First author is the confirmed corresponding author on the clean PDF"
        if i + 1 < len(lines) and "subject to author agreement" in lines[i + 1]:
            lines[i + 1] = "  (`fariq@renaro.my.id`)."
    if line.startswith("**Publication candidate") and "technically complete" in line:
        lines[i] = "**ZENODO PACKAGE READY - AWAITING MANUAL UPLOAD.** The manuscript is not"
        if i + 1 < len(lines):
            lines[i + 1] = "peer-reviewed, not accepted, not deposited and has no DOI. Author metadata and"
        if i + 2 < len(lines):
            lines[i + 2] = "declarations are confirmed by the coordinator; no upload or submission was"
        if i + 3 < len(lines):
            lines[i + 3] = "performed."
p.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("patched")
