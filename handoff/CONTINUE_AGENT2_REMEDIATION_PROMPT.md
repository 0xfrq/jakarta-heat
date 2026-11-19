# Prompt untuk AI penerus Agent 2

Anda meneruskan REMEDIATION SPRINT Jakarta Heat Inequality Mapper sebagai
**Agent2**, bukan memulai audit baru. Bekerja dan menulis hanya di
`D:\jakarta-heat-agent2`. Auditor berada di `D:\jakarta-heat\audit` dan read-only.
Jangan memakai path lama `D:\jakarta-heat-auditor` yang tidak ada. Jangan commit,
push, reset, clean, mengubah baseline resmi, atau menulis ke worktree lain tanpa
otorisasi. Pengguna menghentikan agen sebelumnya untuk memindahkan tugas karena
limit; lanjutkan pekerjaan konkret dari checkpoint ini.

Baca dahulu tujuh sumber wajib auditor: `ISSUE_REGISTER.csv`,
`INDEPENDENT_AUDIT_REPORT.md`, `OWNER_TASKS.md`, `REMEDIATION_ROADMAP.md`,
`NOVELTY_REVIEW.md`, `ACCEPTANCE_MATRIX.md`, `RELEASE_GATE.md`. Kemudian baca
`handoff/REMEDIATION_AGENT2.md` untuk status per isu, bukti, koreksi, dan blocker.
Isu milik Anda: **AC-01, AC-02, DM-01, TM-02, BG-01, IN-01, IN-02**, semuanyaP1.
Tidak ada P0 terbukti dalam register. Pertahankan batas kepemilikan Agent1/3.

## Hasil nyata yang sudah tersedia — jangan ulang dari nol

- Jalur `aggregate_demographics.py` menghitung dukungan piksel/luas, QGIS hybrid
  dan fractional; empty support menjadi null, valid zero tetap berbeda. Kontrak
  `person2_contracts.py` dan CLI `07_integrate_spatial.py` mendukung null terjelaskan
  tanpa mengubah jalur legacy.
- Dua raster usia **real** buffered1km telah diunduh ke
  `data/raw/worldpop/age_buffered/`, dengan request/manifest/hash. Produk2024
  R2025A dan74.429 piksel valid lama per raster identik. Jangan download ulang
  atau menimpa sumber.13 dari19 age gaps pulih; enam sel total/usia tetap null.
- Original-mask agregasi disimpan di `outputs/qa/remediation_agent2/original_masks/`.
  Koreksi terpisah di `data/processed/demographic_support.csv`,
  `demographic_features_corrected.csv`, `spatial_features_corrected.csv`,
  `final_model_features_corrected.csv`. Seluruh2765 ID dipertahankan.
- Replay independen formula baseline tanpa import frozen `jhim` sudah membuktikan
  skor/peringkat baseline cocok. Proposal common set2536 vs2538. M4 top10 retains
 253/254, Jaccard.992157; R039_C051 keluar, R056_C043 masuk. Fixed-set top tetap.
  Fractional setelah buffer swaps16, Jaccard.881481. Semua top5/10/20 danID ada
  di tabelQA. Jangan memaksa angka lama2526/17entrants setelah sumber diperbaiki.
- Semua1015 kandidat taman punya rawtags/status bukti;20 prioritas auditor tetap
  unresolved jika tidak ada bukti; mencakup91/254 top origins. Empat sumber
  municipal hanya konteks, **bukan** bukti gate/public opening. GPKG verified
  entrances sengaja kosong. Dua tujuan kandidat berbeda per asal telah dirutekan;
 2526 asal punya alternatif kedua. Positive-only adalah stress cakupan tujuan.
- Skrining gate/konektor mempertahankan snap-node asli:167 origin dan78 park
  connectors konflik node larangan; konservatif226→407 missing routes. Unknown
  conditional/physical access tetap unknown. Fixed-set M4 Jaccard.895582.
- Pilot historis3AOI×2tanggal benar-benar dicoba: semua HTTP406, arsip tersedia.
  Tidak ada bukti stabilitas temporal. TM-01 belum disahkan; rekomendasi mixed
 2024 raster/2026 OSM proxy, tanpa klaim actual2024 public access.
- Tes awal38+7subtests; tes terakhir yang **benar-benar dijalankan**49+7subtests
  lulus. `tests/test_agent2_remediation.py` dibuat **sesudahnya, belum dijalankan**.
- `requirements.lock` union pin A2/A3 tanpa konflik. Fresh environment
  `.venv/reproduction` sudah dibuat dan instalasi lock sukses, tetapi pipcheck/
  fresh tests/full offline twice belum dijalankan.
- `scripts/run_reproduction.ps1`, `agent2_freeze_inputs.py` sudah ditulis,
  **belum diuji**. Frozen input manifest/bundle belum dibuat. Raw/cache/graph
  lokal sudah disalin hash-preserving, tetapi gitignored dan perlu dibundel.

## Kerjakan berikutnya, berurutan

1. Periksa gitstatus dan proses agar tidak menimpa pekerjaan. Tidak ada proses
   diketahui masih berjalan saat checkpoint. Jangan menghapus perubahan lama.
2. Ada perubahan terakhir setelah tes: support-area dihitung union proyeksi yang
   diintersect kembali dengan polygonUTM agar fraction tidak>1. Agregasi original
   dan buffered sudah diulang sukses. **Rerun integrasi dan effects**, karena
   spatial/full corrected masih versi sebelum perubahan metadata ini:

```powershell
.venv/Scripts/python scripts/07_integrate_spatial.py --demographics data/processed/demographic_features_corrected.csv --support data/processed/demographic_support.csv
.venv/Scripts/python scripts/agent2_park_evidence.py
.venv/Scripts/python scripts/agent2_remediation_effects.py
.venv/reproduction/Scripts/python -m pip check
.venv/reproduction/Scripts/python -m pytest tests/test_demographic_support.py tests/test_agent2_remediation.py tests/test_agent2_gis.py tests/test_walking_pipeline.py -q -p no:cacheprovider --junitxml=outputs/qa/remediation_agent2/fresh_environment_tests.xml
```

   Park script terakhir ditambah offline replay. Pastikan tidak ada HTTP kecuali
   `--refresh-evidence`. Perbaikan mengosongkan publication_date Taman Walang
   yang sebelumnya tidak terbukti; arsipJSON lama masih berisi date itu sampai
   rerun. Jangan mengarang tanggal. Effects terakhir ditambah `*_raw`, pembaruan
   flag age-zero, GPKG corrected dan figure; **tambahan ini belum dieksekusi**.
   Karena itu GPKG corrected dan figure belum ada pada checkpoint; jangan
   melemahkan tes yang mengharapkan keduanya—jalankan generatornya.
3. Perbaiki bug nyata bila tes gagal; jangan mengubah temuan ilmiah demi angka
   target. Inspeksi gambar `disputed_connectors.png` dan figure perubahan
   demografi/agregasi yang baru dihasilkan memakai image viewer. Semua kandidat
   unknown tetap unknown, bukan taman publik terkonfirmasi.
4. Setelah evidence offline konsisten, bootstrap:
   `.venv/reproduction/Scripts/python scripts/agent2_freeze_inputs.py --freeze`.
   Periksa INPUTS dan hash manifest; jangan mem-freeze sumber yang tidak benar.
   Jalankan `scripts/run_reproduction.ps1 -Scope Agent2` dalam freshenv dua kali
   secara berurutan dengan log terpisah. Bandingkan tabel numerik/ID/missingness/
   state dan geometriGPKG; pisahkan timestamp/serialization dari semantic equality.
   Perbaiki script bila perlu. Bungkus frozen input bundle dengan `--bundle` dan
   uji restore/check ke lokasi aman jika feasible; jangan menimpa input berbeda.
5. Buat `docs/REPRODUCE.md`: Windows/Python/native versions, install lock, hashes,
   offline frozen-input lane versus online refresh, lokasi bundle dan lisensi,
   semua commands serta hasil aktual. Entry point ini bukan full raw-to-paper
   consolidated pass. Perbarui dictionary/manifest versi output dan sediakan
   registry skenario/periode variabel untuk Agent3 bila belum ada.
6. Siapkan `docs/integration_manifest.json` dan checklist antarmuka: source hashes,
   SHA+dirty inventories, corrected canonical paths, supportnullable fields,
   RS aliases, README conflict, dashboard rename, frozen-input availability.
   Jangan mengimport paketPython dari frozenQA. **IN-01 tetap BLOCKED** tanpa
   otorisasi commit/kandidatgabungan dan finalA1/A3/DM-02/scientific decisions.
   Jangan menyalin/menimpa kode Agent3 atau mengklaim combinedtests sudah jalan.
   `-Scope Consolidated` harus fail jelas bila fileA1/A3 belum ada.
7. Lengkapi `handoff/REMEDIATION_AGENT2.md` per acceptance, hasil tes dan efek akhir.
   Tambahkan koreksi pada `handoff/AGENT2_HANDOFF.md` yang masih menyatakan
   handover sebelumnya DONE; dokumen lama tidak menggambarkan status remediasi.
   Jangan memakai renderer lama yang menimpa koreksi baru tanpa meninjaunya.
8. Akhiri dengan laporan BahasaIndonesia: tujuhisu, yang closed dengan bukti,
   yang partial/blocked dan mengapa, files, actualtests, efek ilmiah, integrasi
   Agent3, keputusanmanusia dan kesiapan integrasi. Jangan deklarasi paper-ready
   atau menutup gate independen hanya karena tests pass.

## Batas penutupan yang harus jujur

DM-01 paling dekat ke PASS implementasi setelah finalverification. AC-01/AC-02
masih PARTIAL karena public opening/gates/physicallegal crossing dan primary
policy belum disahkan. BG-01 analisis sudah jalan, tetapi primaryallocation/
coverage/countdensity perlu keputusan. TM-02 BLOCKED untuk historicalclaims;
bisa scope-deferred hanya setelah TM-01 mixedperiod disahkan dan dependentclaims
dihapus. IN-02 feasible dipersiapkan/diuji untuk A2, consolidated gate tetap
bergantung IN-01. Koordinator perlu memilih scope waktu, construct kandidat,
permission policy, aggregation/coverage dan shared eligibility. Agent3 bertanggung
jawab DM-02 propagasi support, MD-03 skenario, UI-01 wording, dan hasil model
resmi. JKT_R037_C062 mempunyai delivered LST/NDVI; jangan sebut RS deliveryfailure.
