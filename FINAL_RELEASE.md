# Rilis Final — Jakarta Heat Priorities v1

**Status:** `PUBLICATION CANDIDATE — ZENODO PACKAGE READY`  
**Tanggal konsolidasi:** 23 November 2026  
**Lokasi tunggal:** `D:\jakarta-heat` (branch `main`)  
**Paper version:** v1, 21 November 2026  
**Sifat:** preprint non-peer-reviewed; belum ada DOI, belum diunggah ke Zenodo.

Dokumen ini adalah peta tunggal untuk seluruh hasil kerja: paper final, source
LaTeX, output riset, bukti audit, dan catatan reproduksi. Semua branch agent,
integrasi, paper, riset, dan audit sudah digabung ke `main`.

---

## 1. Paper final

Paket siap-unggah ada di:

```text
paper/zenodo_preprint/zenodo_release/
```

| File | Isi | Ukuran | SHA-256 |
|---|---|---:|---|
| `Jakarta_Heat_Priorities_Preprint_v1.pdf` | Manuscript utama, **25 halaman**, profil netral | 2.426.183 B | `72e4e50b60716408d3ae60a66da1d422bd1a19e42d62f3d0a72660eb7553a986` |
| `Jakarta_Heat_Priorities_Supplementary_v1.pdf` | Supplementary, **8 halaman** | 801.426 B | `9cd990b91fdc94dad04d5ce5663d42cd80920c8e9ecec8908387133ace096a58` |
| `ZENODO_METADATA.md` | Draft metadata Zenodo | — | — |
| `LICENSE_MANUSCRIPT.txt` | CC BY 4.0 | — | — |
| `UPLOAD_FILE_MANIFEST.sha256` | Checksum paket upload | — | — |
| `RELEASE_README.md` | Petunjuk upload dan scope ilmiah | — | — |

Judul: *From Thermal Hotspots to Spatial Priorities: Attribution and Sensitivity
of Urban Heat Screening in Jakarta*.

Penulis: Muhammad Fariq Faqih (corresponding), Muhammad Alim Mustofa,
Mu'adz Abdulloh — Renaro Lab, Indonesia.

### Source dan versi PDF lain

| Lokasi | Isi |
|---|---|
| `paper/zenodo_preprint/input/Manuscript.tex` | Sumber kanonis manuscript |
| `paper/zenodo_preprint/input/Supplementary.tex` | Sumber kanonis supplementary |
| `paper/zenodo_preprint/input/References.bib` | Bibliografi, 67 referensi tersitasi |
| `paper/zenodo_preprint/input/Figures/` | 10 figure PDF |
| `paper/zenodo_preprint/input/Tables/` | 15 tabel LaTeX |
| `paper/zenodo_preprint/output/pdf/` | PDF netral, internal review, submission candidate, Zenodo |
| `paper/zenodo_preprint/CLAIM_EVIDENCE_MATRIX.csv` | Pemetaan klaim ke bukti RC1 |
| `paper/zenodo_preprint/MANUSCRIPT_STATUS.md` | Status manuskrip dan hal yang masih perlu keputusan manusia |
| `paper/zenodo_preprint/FINAL_PREPRINT_RELEASE_RECORD.md` | Rekaman rilis dan deklarasi |
| `paper/zenodo_preprint/RELEASE_READINESS_REPORT.md` | Hasil pemeriksaan kesiapan rilis |
| `paper/independent_scientific_audit_2026-11-20/` | 18 laporan audit ilmiah independen |

Catatan kecil: `RELEASE_README.md` semula menulis 24 halaman; sudah dikoreksi
menjadi 25 halaman agar konsisten dengan PDF final dan `COMPILATION_REPORT.md`.
Checksum README di `UPLOAD_FILE_MANIFEST.sha256` sudah diperbarui.

---

## 2. Output riset

| Lokasi | Isi | Jumlah |
|---|---|---:|
| `outputs/tables/` | Perbandingan model, Jaccard/Kendall/Spearman, sensitivitas M2–M4, LISA, top-10 per model, transisi rank | 29 CSV |
| `outputs/figures/` | Figure PNG + SVG untuk paper | 26 file |
| `outputs/maps/` | Peta hasil analisis | 5 file |
| `outputs/gis/` | `priority_models.gpkg` | 1 GeoPackage |
| `outputs/remediation/` | Output remediasi Agent 2 dan skenario | 103 file |
| `outputs/qa/` | Bukti QA Agent 1/2/3, RC1, RC2, screenshot dashboard | 468 file |
| `data/processed/modeling/` | `priority_models.csv`, `merged_grid.csv`, `lisa_m1–m4.csv`, sensitivity, manifest | 14 file |
| `docs/` | Metode, spesifikasi model, kebijakan taman, agregasi populasi, keputusan riset, reproduksi | 31 file |
| `handoff/` | Handoff Agent 1/2/3, RC1, RC2, issue ledger | 20 file |
| `audit/` | Audit independen dan bukti (dipertahankan read-only, di-ignore Git) | 396 file |

Output kunci yang paling sering dipakai:

- `data/processed/modeling/priority_models.csv` — skor dan rank M1–M4.
- `data/processed/modeling/merged_grid.csv` — grid analisis gabungan.
- `data/processed/modeling/lisa_m4.csv` — hasil LISA M4.
- `outputs/tables/model_comparison.csv` — perbandingan model.
- `outputs/tables/sensitivity_m4_summary.csv` — sensitivitas M4.
- `outputs/tables/lisa_cluster_counts.csv` — hitungan klaster LISA.

---

## 3. Struktur satu folder

```text
D:\jakarta-heat\
├── FINAL_RELEASE.md          ← dokumen ini
├── README.md                 ← README proyek
├── paper\                    ← paper final, source LaTeX, audit ilmiah
├── data\processed\           ← data analisis dan output model kanonis
├── outputs\                  ← tabel, figure, peta, GIS, QA, remediasi
├── docs\                     ← metode, spesifikasi, keputusan, reproduksi
├── handoff\                  ← handoff antar-agent dan RC1/RC2
├── audit\                    ← audit independen (read-only, ignored)
├── dashboard\                ← aplikasi Streamlit
├── scripts\, script\, jhim\  ← kode pipeline dan model
├── tests\                    ← test suite
└── qgis\                     ← berkas QGIS
```

---

## 4. Status integrasi dan verifikasi

| Item | Status |
|---|---|
| Agent 1 (remote sensing) | Digabung ke RC1 |
| Agent 2 (populasi, OSM, taman) | Digabung ke RC1, diremediasi |
| Agent 3 (model, LISA, dashboard) | Digabung ke RC1, diremediasi |
| RC1 | Baseline ilmiah beku `3b8ed05` |
| RC2 | Engineering PASS; scientific HOLD |
| Paper v1 | Selesai secara teknis; publication candidate |
| Test suite RC2 | 236 test + 7 subtest, 0 gagal (clean checkout) |
| Replay RC2 | 63 tabel/metadata, selisih numerik maksimum 0.0 |
| Push ke origin | Belum dilakukan |

RC2 hanya menutup masalah portabilitas dan provenance engineering. RC2 **tidak**
menandatangani keputusan ilmiah, bobot model, threshold, klaim akses, atau
kesimpulan kebijakan.

---

## 5. Cara mereproduksi

```powershell
cd D:\jakarta-heat
.\.venv\Scripts\Activate.ps1

# test suite
python -m pytest -q

# pipeline model dan output
python scripts\run_agent3_pipeline.py

# verifikasi RC2
python scripts\verify_rc2.py
```

Panduan lengkap:

- `docs/REPRODUCE.md`
- `docs/RC2_REPRODUCE.md`
- `docs/AGENT3_REMEDIATION_REPRODUCE.md`
- `paper/zenodo_preprint/README.md` (build LaTeX)

Build paper memakai template Manuscript Multi-Target LaTeX v1.0.0 dan
TinyTeX/TeX Live 2026. Sumber kanonis hanya `input/Manuscript.tex`; jangan membuat
salinan manuscript kedua.

Verifikasi checksum paket paper:

```powershell
cd paper\zenodo_preprint\zenodo_release
Get-Content UPLOAD_FILE_MANIFEST.sha256 | ForEach-Object {
  $p = $_ -split '\s+', 2
  $actual = (Get-FileHash -Algorithm SHA256 $p[1]).Hash.ToLower()
  if ($actual -ne $p[0]) { "MISMATCH: $($p[1])" } else { "OK: $($p[1])" }
}
```

---

## 6. Batasan ilmiah yang tetap berlaku

Ini bukan daftar bug; ini batasan yang harus tetap disebut saat paper dipakai.

- Paper adalah **preprint non-peer-reviewed**, bukan publikasi final.
- Belum ada DOI; DOI hanya terbit setelah Zenodo mempublikasikan record.
- Provenance akuisisi Landsat tidak terverifikasi (RS-01 diterima sebagai
  limitasi untuk preprint ini).
- Akses taman adalah **modeled network access**, bukan entrance publik yang
  terverifikasi; 0 entrance terverifikasi.
- Sampel komparasi common adalah 2.536 grid (2.535 untuk LISA setelah pulau
  dikeluarkan); bukan estimasi prevalensi seluruh Jakarta.
- M4 adalah indeks screening eksploratif heat–population–park deficit; bukan
  model kesehatan, risiko, atau kausalitas.
- Term taman dapat mendominasi top decile secara mekanis; ini temuan metodologis,
  bukan bukti ketidakpedulian taman.
- Keputusan ilmiah D1–D13 dan QA-01 masih memerlukan sign-off manusia.

---

## 7. Riwayat konsolidasi

Branch yang sudah digabung ke `main`:

```text
agent/person1
agent/person2
agent/person3
integration/rc1
integration/rc2
paper/zenodo-draft
research/m4-review
audit/rc1-review
```

Commit kunci:

| Commit | Peran |
|---|---|
| `3439f38` | RC2 final, engineering verification |
| `9e6bc51` | Paket paper v1 dan audit ilmiah |
| `0ef2da5` | Merge final paper + RC2 ke `main` |

Worktree agent masih ada di `D:\jakarta-heat-agent1`, `-agent2`, `-agent3`, dan
lain-lain. Semuanya sudah bersih dan isinya sudah masuk `main`, jadi worktree
tersebut dapat dihapus setelah verifikasi. Repo tunggal yang dipakai adalah
`D:\jakarta-heat`.
