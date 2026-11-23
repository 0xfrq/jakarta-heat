from pathlib import Path
p = Path(r"D:\jakarta-heat-paper\paper\zenodo_preprint\MANUSCRIPT_STATUS.md")
s = p.read_text(encoding="utf-8")
old = "| LISA significant (directed/999/BH) | 663 | `lisa_tail_permutation_sensitivity.csv` |"
new = ("| LISA significant (two-sided/9,999/BH, primary) | 493 | `lisa_tail_permutation_sensitivity.csv` |\n"
       "| LISA significant (directed/999/BH, historical) | 663 | idem |")
if old in s:
    s = s.replace(old, new, 1)
else:
    lines = s.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("| LISA significant (directed/999/BH)"):
            lines[i:i+1] = [new.splitlines()[0], new.splitlines()[1].replace("| LISA significant (directed/999/BH, historical) | 663 | idem |", "| LISA significant (directed/999/BH) | 663 | idem |")]
            break
    s = "\n".join(lines)

old2 = "- Publication candidate PDF: 23 halaman."
new2 = "- Publication candidate PDF: 23 halaman.\n- Internal review PDF: 23 halaman."
if old2 in s:
    s = s.replace(old2, new2, 1)
else:
    lines = s.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("- Publication candidate PDF:"):
            lines[i] = new2
            break
    s = "\n".join(lines)
p.write_text(s, encoding="utf-8")
print("updated")
