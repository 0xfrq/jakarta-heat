from pathlib import Path
p = Path(r"D:\jakarta-heat-paper\paper\zenodo_preprint\COMPILATION_REPORT.md")
lines = p.read_text(encoding="utf-8").splitlines()
for i, line in enumerate(lines):
    if line.startswith("- Main manuscript: one overfull"):
        lines[i] = "- Main manuscript: no overfull `\\hbox`; one underfull `\\hbox` of"
        if i + 1 < len(lines):
            lines[i + 1] = "  badness 6927 in the declarations region; visually acceptable in the rendered"
        if i + 2 < len(lines) and "not visible" in lines[i + 2]:
            lines[i + 2] = "  PDF."
p.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("warnings patched")
