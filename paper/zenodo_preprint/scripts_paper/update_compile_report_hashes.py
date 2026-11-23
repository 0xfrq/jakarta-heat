from pathlib import Path
p = Path(r"D:\jakarta-heat-paper\paper\zenodo_preprint\COMPILATION_REPORT.md")
lines = p.read_text(encoding="utf-8").splitlines()
new = {
    "Manuscript-submission-candidate.pdf": "| `Manuscript-submission-candidate.pdf` | 23 | 2,416,403 bytes | `66302DA1618D519A39152CAE618981AF4FAB3D30B42EC47E49A6A5AF5E470066` |",
    "Manuscript-internal-review.pdf": "| `Manuscript-internal-review.pdf` | 23 | 2,416,668 bytes | `34F84957BE807149DF9BD333A261DEA1902987C92DAC08B6F83878934CC7666D` |",
    "Supplementary-submission-candidate.pdf": "| `Supplementary-submission-candidate.pdf` | 7 | 799,191 bytes | `1CD6992723632236D61F4E0A85EA054268E373EFEE02A3B6277843ABB82A2675` |",
}
for i, line in enumerate(lines):
    for name, replacement in new.items():
        if line.startswith("| `" + name + "`"):
            lines[i] = replacement
p.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("updated")
