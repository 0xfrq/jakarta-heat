from pathlib import Path
p = Path(r"D:\jakarta-heat-paper\paper\zenodo_preprint\MANUSCRIPT_STATUS.md")
s = p.read_text(encoding="utf-8")
old = """ORCID tidak dimasukkan karena belum diberikan. CRediT/Author Contributions tidak
dimasukkan ke PDF publik dan tetap menunggu persetujuan ketiga author."""
new = """ORCID tidak dimasukkan karena belum diberikan. Author Contributions memakai
pernyataan kolektif yang disetujui oleh koordinator; CRediT individual tidak
dibuat."""
if old in s:
    s = s.replace(old, new)
old2 = """**Independent audit 20 November 2026:** Table 7 sebelumnya mencampur nilai
M3-relative dengan M4-relative. Manuscript sudah diperbaiki: Table 7 sekarang
M3-relative dan Table 8 M4-relative. Defect ini ditutup di claim register,
tetapi status ilmiah tetap **COMPLETE DRAFT / PENDING SCIENTIFIC APPROVAL**
karena D1�?"D13, RS-01 dan interpretasi konstruk belum ditandatangani. Detail ada
di `paper/independent_scientific_audit_2026-11-20/INDEPENDENT_SCIENTIFIC_AUDIT.md`.
Jangan upload ke Zenodo sebelum keputusan manusia dan final re-audit."""
new2 = """**Independent audit 20 November 2026:** Table 7 sebelumnya mencampur nilai
M3-relative dengan M4-relative. Manuscript sudah diperbaiki: Table 7 sekarang
M3-relative dan Table 8 M4-relative. D1–D13, deklarasi author dan penerimaan
RS-01 tercatat pada dokumen final. Paket Zenodo sudah siap untuk review manual;
jangan upload sebelum koordinator memverifikasi metadata dan record."""
if old2 in s:
    s = s.replace(old2, new2)
else:
    marker = "**Independent audit 20 November 2026:**"
    if marker in s:
        head, rest = s.split(marker, 1)
        para_end = rest.find("\n\n")
        s = head + new2 + rest[para_end:] if para_end >= 0 else head + new2
p.write_text(s, encoding="utf-8")
print("status text patched")
