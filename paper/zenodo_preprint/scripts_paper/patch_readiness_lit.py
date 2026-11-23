from pathlib import Path
p = Path(r"D:\jakarta-heat-paper\paper\zenodo_preprint\RELEASE_READINESS_REPORT.md")
lines = p.read_text(encoding="utf-8").splitlines()
for i, line in enumerate(lines):
    if line.startswith("| Main PDF builds"):
        lines[i] = "| Main PDF builds | Pass - 25 pages |"
    if line.startswith("- Main PDF:"):
        lines[i] = "- Main PDF: **25 pages**, 2,426,183 bytes, SHA-256"
        if i + 1 < len(lines):
            lines[i + 1] = "  `72e4e50b60716408d3ae60a66da1d422bd1a19e42d62f3d0a72660eb7553a986`"
    if "AWAITING MANUAL UPLOAD" in line:
        lines[i] = line.replace("AWAITING MANUAL UPLOAD", "FINAL LITERATURE REVISION COMPLETE")
p.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("readiness patched")
