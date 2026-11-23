from pathlib import Path
p = Path(r"D:\jakarta-heat-paper\paper\zenodo_preprint\COMPILATION_REPORT.md")
lines = p.read_text(encoding="utf-8").splitlines()
for i, line in enumerate(lines):
    if line.startswith("| `Manuscript-submission-candidate.pdf`"):
        lines[i] = "| `Manuscript-submission-candidate.pdf` | 25 | 2,426,183 bytes | `72E4E50B60716408D3AE60A66DA1D422BD1A19E42D62F3D0A72660EB7553A986` |"
    if line.startswith("| `Manuscript-internal-review.pdf`"):
        lines[i] = "| `Manuscript-internal-review.pdf` | 25 | 2,426,719 bytes | `234BC4F7780D49A73844E4390B3E5FF04BFBB6B4C7876E2C6EDF2B1EBA0AB47B` |"
p.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("compile table patched")
