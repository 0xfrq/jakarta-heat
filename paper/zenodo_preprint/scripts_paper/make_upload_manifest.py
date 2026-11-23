import hashlib
from pathlib import Path

pkg = Path(r"D:\jakarta-heat-paper\paper\zenodo_preprint\zenodo_release")
files = [
    "Jakarta_Heat_Priorities_Preprint_v1.pdf",
    "Jakarta_Heat_Priorities_Supplementary_v1.pdf",
    "ZENODO_METADATA.md",
    "LICENSE_MANUSCRIPT.txt",
    "RELEASE_README.md",
]
lines = []
for name in files:
    h = hashlib.sha256((pkg / name).read_bytes()).hexdigest()
    lines.append(f"{h}  {name}")
(pkg / "UPLOAD_FILE_MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
