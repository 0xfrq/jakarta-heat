# Status Manuskrip â€” Handoff untuk Koordinator Riset

**Tanggal:** 21 November 2026 WIB
**Status keseluruhan:** `PUBLICATION CANDIDATE — TECHNICALLY COMPLETE / HUMAN AUTHOR CONFIRMATION REQUIRED`
**Bukan:** `READY FOR PUBLICATION`
**Branch:** `paper/zenodo-draft`
**Frozen evidence:** RC1 `3b8ed05be92c35bbb2b3a617688540ee856b11c8`

## 1. Ringkasan eksekutif

Manuskrip LaTeX lengkap sudah ditulis, disusun dengan template Zenodo v1.0.0,
dan dikompilasi menjadi PDF 25 halaman (candidate dan internal review) serta suplemen 8
halaman. Isi ilmiah menggunakan RC1 sebagai referensi beku dan tidak mencampur
angka dari RC2. Semua angka utama dapat dilacak ke tabel RC1 melalui
`CLAIM_EVIDENCE_MATRIX.csv`.

Naskah adalah publication candidate yang lengkap secara teknis. Yang masih
memerlukan konfirmasi manusia adalah persetujuan author, kontribusi, funding,
konflik kepentingan, lisensi, dan penerimaan limitasi provenance Landsat. Naskah
tidak boleh dinyatakan publikasi final, peer-reviewed, atau didukung klaim
kesehatan/akses publik terverifikasi.

## 1b. Author dan afiliasi

- Muhammad Fariq Faqih - `fariq@renaro.my.id` (corresponding author; confirmed by coordinator)
- Muhammad Alim Mustofa â€” `alim@renaro.my.id`
- Mu'adz Abdulloh â€” `muadz@renaro.my.id`
- Afiliasi: **Renaro Lab, Indonesia**, <https://renaro.my.id>.

ORCID tidak dimasukkan karena belum diberikan. Author Contributions memakai
pernyataan kolektif yang disetujui oleh koordinator; CRediT individual tidak
dibuat.

## 2. Judul dan posisi

**Judul kerja:** *From Thermal Hotspots to Spatial Priorities: Attribution and
Sensitivity of Urban Heat Screening in Jakarta*

Posisi: **comparative spatial prioritization and uncertainty assessment**.
Kontribusi yang dipertahankan:

1. **Metodologis:** atribusi Shapley atas perubahan peringkat M3â†’M4 dan
   envelope sensitivitas yang memisahkan construct change dari reweighting.
2. **Empiris Jakarta:** temuan bahwa age count hampir kolinear dengan total
   population; age share mengubah objektif dan geografi; park term dapat
   mendominasi top decile secara mekanis.
3. **Reproducibility:** artefak RC1 dengan hash, replay 63 tabel, dan
   claim-evidence register.
4. **Negative/limitation findings:** park term bukan bukti ketidakpedulian
   taman; LISA sangat sensitif terhadap konvensi; common subset bukan Jakarta.

Kontribusi **bukan** "first integrated framework", bukan algoritma baru, dan
bukan validasi model kesehatan.

## 3. Yang sudah selesai

### 3.1 Naskah

- Abstract naratif sekitar 260 kata dengan angka RC1 yang terverifikasi.
- 1 Introduction, 2 Related Work, 3 Study Area and Data, 4 Methods lengkap
  dengan formula M1â€“M4, normalisasi, eligibility, Jaccard, Shapley, skenario,
  Moran/LISA, dan reproducibility.
- 5 Results dengan 11 subbagian, 6 figur utama, 11 tabel utama.
- 6 Discussion, 7 Limitations (17 item spesifik), 8 Conclusion.
- Author Contributions (collective statement), Funding, Conflicts of Interest,
  Data and Code Availability, Acknowledgements, AI-assisted tools disclosure dan
  CC BY 4.0 statement tercantum di PDF publik.
- 67 referensi cited dan terverifikasi (67 entri database; semua entri dikutip); tidak ada placeholder citation.
- Publication candidate tanpa draft banner; versi internal review memakai
  wrapper dengan identifier internal singkat.

### 3.2 Figur

- Fig. 1: LST dan NDVI.
- Fig. 2: population dan park distance.
- Fig. 3: M1 vs M4 top-decile maps.
- Fig. 4: rank displacement.
- Fig. 5: Shapley attribution dan scenario-family envelope.
- Fig. 6: LISA map dan convention counts.
- Fig. S1â€“S3: score distributions, exclusion map, park inventory.

Semua figur dibuat dari tabel/GIS RC1, bukan screenshot dashboard, dan bukan
data sintetis.

### 3.3 Tabel

- Table 1: literature comparison.
- Table 2: park evidence states.
- Table 3: data sources and reference periods.
- Table 4: sample eligibility.
- Table 5: model definitions.
- Table 6: pairwise model comparison.
- Table 7: incremental attribution relative to M3.
- Table 8: construct/ablation comparisons relative to M4.
- Table 9: selection profile.
- Table 10: LISA sensitivity.
- Table 11: scenario-family sensitivity.
- Table S1â€“S6: data quality, three-budget sensitivity, city composition,
  LISA counts, provenance.

### 3.4 Build

- Publication candidate PDF: 25 halaman.
- Internal review PDF: 25 halaman.
- Supplementary PDF: 8 halaman.
- Compiler: TinyTeX/TeX Live 2026, pdfTeX 1.40.29, latexmk 4.88.
- Tidak ada undefined citation/reference.
- Satu overfull hbox 2.03 pt (tidak material).
- Detail: `COMPILATION_REPORT.md`.

## 4. Angka kunci yang sudah diverifikasi

| Klaim | Nilai | Bukti |
|---|---:|---|
| Master grid | 2.765 | `grid_master.csv`, `priority_models.csv` |
| Common comparison set | 2.536 | `priority_models.csv`, `eligibility_by_model.csv` |
| Excluded | 229 (8,28%) | audit + eligibility |
| M1/M2 eligible | 2.764 | `eligibility_by_model.csv` |
| M3 eligible | 2.758 | idem |
| Top-decile budget | 254 | `ceil(0.1 Ã— 2536)` |
| M1â€“M4 Jaccard (10%) | 0,384 | `jaccard_matrix.csv` |
| Mean absolute M1â€“M4 rank shift | 307,4 | `rank_movement.csv` |
| M3â€“M4 Jaccard | 0,411 | `jaccard_matrix.csv` |
| Shapley park / reweight / age | 85,46% / 13,25% / 1,29% | `rank_change_attribution.csv` |
| Age count vs total population Spearman | 0,999479 | audit |
| Total-count swap Jaccard | 0,976654 | `ablation_comparison.csv` |
| Vulnerable-share Jaccard | 0,347480 | idem |
| M4 top cutoff | 0,873739849 | `priority_models.csv` |
| Max score â‰¤500 m | 0,869648776 | idem |
| Near-park cells in top 254 | 0 / 537 | idem |
| Closest top cell | 638,2 m | idem |
| Top cells at 1.000 m cap | 174 / 254 | idem |
| Positive-tag-only Jaccard | 0,420168 | route scenario tables |
| Conservative fixed Jaccard | 0,896 | audit / route tables |
| Excluded population | 463.697 (4,22%) | selection profile |
| Moran M1â€“M4 | 0,6711 / 0,6540 / 0,6644 / 0,5930 | `moran_global.csv` |
| LISA significant (two-sided/9,999/BH, primary) | 493 | `lisa_tail_permutation_sensitivity.csv` |
| LISA significant (directed/999/BH, historical) | 663 | idem |
| LISA significant (two-sided/999/BH) | 496 | idem |
| LISA significant (BY/999) | 0 (resolution artifact) | idem |

## 4b. Status claim-evidence register

CLAIM_EVIDENCE_MATRIX.csv berisi 42 klaim: **39 VERIFIED**, **2 PROVISIONAL**
(kontribusi/positioning dan batas interpretasi), dan **1 BLOCKED** (lineage
Landsat RS-01). Klaim BLOCKED tetap boleh muncul di naskah hanya sebagai
keterbatasan eksplisit, bukan sebagai hasil terverifikasi.

**Independent audit 20 November 2026:** Table 7 sebelumnya mencampur nilai
M3-relative dengan M4-relative. Manuscript sudah diperbaiki: Table 7 sekarang
M3-relative dan Table 8 M4-relative. D1–D13, deklarasi author dan penerimaan
RS-01 tercatat pada dokumen final. Paket Zenodo sudah siap untuk review manual;
jangan upload sebelum koordinator memverifikasi metadata dan record.

## 5. Klaim yang sengaja ditahan atau dihapus

- "M4 adalah model age-vulnerability" â†’ **dihapus**. M4 adalah count-based
  exposure index; age share adalah estimand berbeda.
- "Top-priority cells lack parks" sebagai temuan empiris â†’ **dihapus**.
  Fenomena cutoff adalah properti aritmetik indeks dan input observasi.
- "M4 lebih baik dari M1â€“M3" â†’ **tidak diklaim**; tidak ada validasi eksternal.
- "Akses publik 2024 terverifikasi" â†’ **tidak diklaim**; 0 verified access,
  0 verified entrance.
- "Jakarta-wide" â†’ **tidak diklaim**; common subset 2.536, excluded 229.
- "p = 0" / "significant everywhere" â†’ **tidak diklaim**; 0,001 adalah
  resolution limit.
- "M4 meningkatkan outcome kesehatan/kebijakan" â†’ **tidak diklaim**.
- "First integrated framework" â†’ **tidak diklaim**; prior art sudah ada.

## 6. Keputusan manusia yang masih diperlukan

Mengacu pada `RC1_SCIENTIFIC_DECISIONS.md` (auditor), keputusan berikut belum
ditandatangani:

1. **D1 â€” Periode rujukan:** setujui mixed-period candidate proxy; larang klaim
   2024 public access/2026 heat.
2. **D2 â€” Historical OSM:** setujui claim withdrawal; tidak ada bukti stabilitas
   temporal.
3. **D3 â€” Support semantics:** terima null untuk no-support; jangan imputasi
   enam grid tanpa sumber.
4. **D4 â€” Konstruk M4:** relabel sebagai exposure-oriented screening index ATAU
   pisahkan heat+population / age composition / park access ATAU revisi
   bobot/cap dan ulang.
5. **D5 â€” Count vs share:** nyatakan tujuan estimand secara eksplisit.
6. **D6 â€” Agregasi populasi:** pilih hybrid atau fractional sebagai primary;
   laporkan keduanya.
7. **D7 â€” Thermal support threshold:** setujui 0,50 sebagai primary dengan
   sensitivitas 0,25/strict.
8. **D8 â€” Akses/route:** terima candidate proxy; tidak ada klaim legal/public.
9. **D9 â€” Common set:** setujui 2.536 dan selection policy; laporkan common vs
   full-area.
10. **D10 â€” Spatial inference:** pre-specify konvensi LISA primary; laporkan
    range.
11. **D11 â€” DW categorical deferral:** tandatangani deferral atau sediakan label.
12. **D12 â€” Novelty/claim scope:** setujui kontribusi attribution/uncertainty;
    hapus klaim "first".
13. **D13 - Final release:** paket Zenodo siap; upload manual dan review record
    dilakukan oleh koordinator. Tidak ada DOI sebelum deposit.
## 7. Dependensi RC2

RC2 belum digunakan sebagai sumber angka. Jika RC2 menjadi tersedia, langkah
yang diperlukan:

1. Verifikasi identitas Git dan hash implementasi RC2.
2. Bandingkan eligibility, skor, rank, top set, dan LISA terhadap RC1.
3. Identifikasi asumsi ilmiah yang berubah (construct, weights, cap, support,
   route policy, aggregation).
4. Perbarui hanya bagian yang didukung bukti terverifikasi.
5. Catat setiap perubahan di `REVISION_LOG.md` dan
   `CLAIM_EVIDENCE_MATRIX.csv`.
6. Jangan menimpa RC1; simpan sebagai pembanding beku.

## 8. Hal yang belum boleh dilakukan

- Jangan upload ke Zenodo atau meminta DOI.
- Jangan menyebut "peer-reviewed", "accepted", "published", atau "approved".
- Jangan menyatakan PDF sudah final secara ilmiah.
- Jangan menambahkan grant/acknowledgement yang belum terverifikasi.
- Jangan mengganti nama author/afiliasi tanpa keputusan ketiga author.
- Jangan menambahkan klaim kesehatan, kausal, atau efektivitas intervensi.

## 9. Rekomendasi langkah berikutnya

1. Koordinator mereview metadata dan melakukan upload manual ke Zenodo.
2. Verifikasi judul, urutan author, afiliasi, email corresponding, lisensi dan
   deklarasi pada record Zenodo.
3. Publikasikan record hanya setelah review manual; DOI baru diklaim setelah
   Zenodo memberikannya.
4. Field verification akses/entrance taman tetap pekerjaan lanjutan, bukan syarat
   paket preprint ini.
5. Jika venue mensyaratkan verifikasi acquisition-level Landsat, siapkan respons
   bukti terpisah; status teknis RS-01 tetap belum terverifikasi.
