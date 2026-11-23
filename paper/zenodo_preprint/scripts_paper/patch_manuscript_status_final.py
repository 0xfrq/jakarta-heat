from pathlib import Path
p = Path(r"D:\jakarta-heat-paper\paper\zenodo_preprint\MANUSCRIPT_STATUS.md")
s = p.read_text(encoding="utf-8")
lines = s.splitlines()
for i, line in enumerate(lines):
    if line.startswith("- Muhammad Fariq Faqih") and "proposed corresponding author" in line:
        lines[i] = "- Muhammad Fariq Faqih - `fariq@renaro.my.id` (corresponding author; confirmed by coordinator)"
    if line.startswith("- Data and Code Availability dan Acknowledgements; Author Contributions,"):
        lines[i] = "- Author Contributions (collective statement), Funding, Conflicts of Interest,"
        if i + 1 < len(lines):
            lines[i + 1] = "  Data and Code Availability, Acknowledgements, AI-assisted tools disclosure dan"
        if i + 2 < len(lines):
            lines[i + 2] = "  CC BY 4.0 statement tercantum di PDF publik."
    if line.startswith("13. **D13") and "Final release" in line:
        lines[i] = "13. **D13 - Final release:** paket Zenodo siap; upload manual dan review record"
        if i + 1 < len(lines):
            lines[i + 1] = "    dilakukan oleh koordinator. Tidak ada DOI sebelum deposit."
s = "\n".join(lines)
old = """1. Tiga author mengisi dan menyetujui Author Contributions serta URK.
2. Koordinator menandatangani D1�?"D12 atau memilih subset yang disetujui.
3. Perbaiki portabilitas RC1 (clean-checkout test, relative paths, receipt
   hashes) sebelum deposit publik.
4. Pulihkan lineage Landsat atau tandatangani claim restriction tertulis.
5. Field-verify akses/entrance untuk kandidat taman berprioritas tinggi."""
new = """1. Koordinator mereview metadata dan melakukan upload manual ke Zenodo.
2. Verifikasi judul, urutan author, afiliasi, email corresponding, lisensi dan
   deklarasi pada record Zenodo.
3. Publikasikan record hanya setelah review manual; DOI baru diklaim setelah
   Zenodo memberikannya.
4. Field verification akses/entrance taman tetap pekerjaan lanjutan, bukan syarat
   paket preprint ini.
5. Jika venue mensyaratkan verifikasi acquisition-level Landsat, siapkan respons
   bukti terpisah; status teknis RS-01 tetap belum terverifikasi."""
if old in s:
    s = s.replace(old, new)
else:
    # Replace the section from the heading onward if exact legacy text is not found.
    marker = "## 9. Rekomendasi langkah berikutnya"
    if marker in s:
        head, _ = s.split(marker, 1)
        s = head + marker + "\n\n" + new + "\n"
p.write_text(s, encoding="utf-8")
print("status patched")
