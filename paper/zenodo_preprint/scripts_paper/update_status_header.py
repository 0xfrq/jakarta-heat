from pathlib import Path
p = Path(r"D:\jakarta-heat-paper\paper\zenodo_preprint\MANUSCRIPT_STATUS.md")
s = p.read_text(encoding="utf-8")
old = "**Status keseluruhan:** `COMPLETE DRAFT / PENDING SCIENTIFIC APPROVAL`"
new = "**Status keseluruhan:** `PUBLICATION CANDIDATE — TECHNICALLY COMPLETE / HUMAN AUTHOR CONFIRMATION REQUIRED`"
if old in s:
    s = s.replace(old, new)
else:
    lines = s.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("**Status keseluruhan:**"):
            lines[i] = new
            break
    s = "\n".join(lines)
old2 = """Status ilmiah tetap **HOLD**. Yang sudah layak adalah draft substantif dan
artefak reproducible; yang belum layak adalah rilis ilmiah final, klaim
kesehatan, klaim akses publik terverifikasi, klaim Jakarta-wide, dan klaim
superioritas model."""
new2 = """Naskah adalah publication candidate yang lengkap secara teknis. Yang masih
memerlukan konfirmasi manusia adalah persetujuan author, kontribusi, funding,
konflik kepentingan, lisensi, dan penerimaan limitasi provenance Landsat. Naskah
tidak boleh dinyatakan publikasi final, peer-reviewed, atau didukung klaim
kesehatan/akses publik terverifikasi."""
s = s.replace(old2, new2)
p.write_text(s, encoding="utf-8")
print(s.splitlines()[2])
