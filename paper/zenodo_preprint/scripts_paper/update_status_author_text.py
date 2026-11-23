from pathlib import Path
p = Path(r"D:\jakarta-heat-paper\paper\zenodo_preprint\MANUSCRIPT_STATUS.md")
s = p.read_text(encoding="utf-8")
old_email = "- Muhammad Fariq Faqih — `fariq@renaro.my.id` (correspondence listed; no single corresponding-author assertion)"
if old_email not in s:
    # The file may use a replacement character for the em dash.
    lines = s.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("- Muhammad Fariq Faqih") and "fariq@renaro.my.id" in line:
            lines[i] = "- Muhammad Fariq Faqih — `fariq@renaro.my.id` (proposed corresponding author; subject to author agreement)"
            break
    s = "\n".join(lines)
else:
    s = s.replace(old_email, "- Muhammad Fariq Faqih — `fariq@renaro.my.id` (proposed corresponding author; subject to author agreement)")
old_aff = "- Afiliasi: **Renaro Lab**, student-led independent AI laboratory,\n  <https://renaro.my.id>."
if old_aff in s:
    s = s.replace(old_aff, "- Afiliasi: **Renaro Lab, Indonesia**, <https://renaro.my.id>.")
else:
    lines = s.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("- Afiliasi:"):
            lines[i] = "- Afiliasi: **Renaro Lab, Indonesia**, <https://renaro.my.id>."
            if i + 1 < len(lines) and lines[i + 1].strip().startswith("<https://renaro.my.id>"):
                lines[i + 1] = ""
            break
    s = "\n".join(lines)
old_note = "ORCID belum diisi karena belum diberikan. Author Contributions masih placeholder\ndan harus disetujui ketiga author."
new_note = "ORCID tidak dimasukkan karena belum diberikan. CRediT/Author Contributions tidak\ndimasukkan ke PDF publik dan tetap menunggu persetujuan ketiga author."
if old_note in s:
    s = s.replace(old_note, new_note)
else:
    lines = s.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("ORCID belum diisi"):
            lines[i] = new_note
            if i + 1 < len(lines) and lines[i + 1].startswith("dan harus disetujui"):
                lines[i + 1] = ""
            break
    s = "\n".join(lines)
p.write_text(s, encoding="utf-8")
print("updated")
