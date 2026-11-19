# Remediasi Agent 1 — Jakarta Heat Inequality Mapper

Tanggal: 20 November 2026 WIB. Worktree: `D:\jakarta-heat-agent1`, branch
`agent/person1`, HEAD sebelum remediasi `cdda42484c6bfc5bceb49093cb4a28be6c59d659`.
Tidak ada commit/push/merge. Semua perubahan dan output baru berada di worktree ini.
Dokumen auditor dibaca dari `D:\jakarta-heat\audit` dan tidak diedit.

Ketujuh sumber wajib dibaca: INDEPENDENT_AUDIT_REPORT.md, ISSUE_REGISTER.csv,
OWNER_TASKS.md, REMEDIATION_ROADMAP.md, NOVELTY_REVIEW.md, ACCEPTANCE_MATRIX.md,
RELEASE_GATE.md. Register berisi 22 isu, tanpa P0 terbukti; owner Agent 1 adalah
**RS-01/P1** dan **DW-01/P2**. Nomor RS-03/RS-04 di bukti RS lama bukan ID register;
kedua koreksinya ditangani di DW-01. Dependensi RS-02, TM-01, MD-03, IN-02 dan
QA-01 ditinjau sesuai antarmuka Agent 1, tanpa mengambil alih owner lain.

| Isu | Status implementasi Agent 1 | Status penerimaan penuh |
|---|---|---|
| RS-01 / P1 | Provenance lokal, pemeriksaan ulang, support tahunan dan alat replay selesai | **BLOCKED** untuk scene/task/AOI historis dan support bulanan; keputusan estimand masih perlu |
| DW-01 / P2 | Status supplementary/R3 partial, denominator dan presisi luas diperbaiki dan diuji | **PARTIAL**; perlu penandatanganan deferral R3 atau ekspor label nyata |
| RS-02 / P1, owner Agent 3 | Bukti support dan keanggotaan kebijakan QA **PASS** untuk bagian Agent 1 | **PARTIAL** lintas tim; ranking skenario/keputusan QA milik Agent 3/koordinator |

PASS di sini berarti bukti lokal implementer. Penutupan register dan keputusan
release tetap melalui re-audit independen (QA-01).

## RS-01 — Complete acquisition provenance and temporal-sampling evidence

**Severity:** P1. **Temuan asli:** Landsat `scene_count` dan `processing_date`
null; tidak ada inventaris lengkap scene, task, versi/geometri AOI, serta distribusi
support bulanan. Raster asli dan agregasi lokal sudah terverifikasi, tetapi tidak
membuktikan asal setiap akuisisi 2024.

**Akar masalah:** resep GEE dan hasil median diarsipkan, namun identitas scene dan
riwayat eksekusi tidak disimpan. Median/observation-count raster tidak memungkinkan
rekonstruksi tanggal atau bobot musim. Mtime berkas bukan tanggal proses GEE.

**Reproduksi blocker:** `ee.Initialize(project='nodemailer-mailer')` pada environment
lokal benar-benar menghasilkan `EEException: Please authorize access to your Earth
Engine account ... earthengine authenticate ...`. Berkas credentials Earth Engine
dan ADC standar tidak ada. Tidak menjalankan autentikasi atau mengirim task.
Jumlah scene asli, tanggal proses dan hash AOI GEE tetap null; angka observasi
maksimum 28 tidak diganti menjadi scene count. DW image count 94 tetap dinyatakan
sebagai ringkasan yang pernah dilaporkan, bukan inventaris yang diverifikasi ulang.

**Berkas diubah/ditambah:**

- `scripts/02e_remote_sensing_remediation.py`: manifest hash input/output/source,
  environment, support tahunan, kebijakan QA, 140 irisan piksel independen, pemeriksaan
  date/collection inventory, pembanding replay raster, dan verifikasi hash tanpa rewrite.
- `scripts/02f_export_remote_sensing_provenance_gee.js`: resep pelengkap untuk replay
  berotorisasi: ID/tanggal/WRS/product scene, monthly clear support, AOI GeoJSON dan
  metadata resep. Task ID/status/waktu proses aktual harus diarsipkan operator.
- `scripts/02_remote_sensing_gee.js`: komentar provenance diperbaiki; logika numerik
  asli tetap. `scripts/02b_aggregate_remote_sensing.py`: hash grid/master/source
  dan direktori output terpisah. `scripts/02d_validate_remote_sensing.py`: QA terisolasi.
- `docs/remote_sensing_export_manifest.json`, `docs/remote_sensing_scene_manifest.csv`,
  `outputs/qa/rs_temporal_support.csv`, `outputs/qa/agent1_remediation/*`:
  bukti aktual lokal dan status unavailable yang eksplisit.
- `docs/landsat_metadata.json`, `docs/dynamic_world_metadata.json`,
  `docs/landsat_quality_report.md`, `docs/remote_sensing_deliverable_status.md`,
  `docs/remote_sensing_reproduction.md`, handoff dan regression tests.

**Koreksi:** estimand dibatasi menjadi mean berbobot luas pada piksel valid dalam
poligon terpotong atas temporal median LST permukaan pagi berlangit cerah.
Tidak ada klaim temperatur udara tahunan, dosis individu, representasi musim atau
validasi kesehatan. Manifest scene hanya header karena belum ada record pulih;
itu berarti unavailable, bukan nol scene. Dua belas baris monthly support memiliki
nilai numerik null dan alasan GEE blocker; bukan observasi bulanan buatan.
Support tahunan mencakup semua 2.765 ID dan ditautkan ke hash raster asli.

**Perintah uji dan hasil:** jalankan dari root dengan `.venv/Scripts/python.exe`:

```powershell
python scripts/02b_aggregate_remote_sensing.py --output-dir data/processed/remote_sensing_remediated
python scripts/02d_validate_remote_sensing.py --rs-dir data/processed/remote_sensing_remediated --output-dir outputs/qa/agent1_remediation/validation
python scripts/02e_remote_sensing_remediation.py
python scripts/02e_remote_sensing_remediation.py --verify
python -m pytest -q -p no:cacheprovider tests/test_remote_sensing_grid.py tests/test_remote_sensing_remediation.py
python -m pip check
node --check scripts/02f_export_remote_sensing_provenance_gee.js
```

40 tests PASS; 49 validator checks, 0 critical failures; 140 nilai pada 35 poligon
PASS dengan perhitungan Shapely independen dari exactextract. Bukti ada di
`outputs/qa/agent1_remediation/pytest.log`, `validator.log`,
`independent_pixel_checks.csv` dan `validation/remote_sensing_qa.json`.
`pip check` tidak menemukan dependency rusak. Pemeriksaan JS adalah syntax-only;
eksekusi server GEE belum diuji. Kasus regresi inventaris menolak tanggal di luar
periode, tanggal tanpa timezone, scene duplikat, dan tidak mengubah header kosong
menjadi keberhasilan akuisisi. Mutasi isi file terdeteksi oleh pemeriksa manifest.

**Efek ilmiah sebelum/sesudah:** LST, NDVI, probabilitas, dukungan observasi, flags
dan semua ID tetap. M1–M4 lokal dihitung ulang dalam memori pada set legacy 2.538 ID:
max perubahan skor 0, perubahan ranking 0; top 5/10/20% tetap seluruhnya
(127/254/508 grid, Jaccard 1). Hasil ini hanya mengukur efek revisi input RS,
bukan perbaikan demografi atau pengesahan model ilmiah final. Nilai rata-rata
jumlah observasi per kota 9,26 Barat; 9,43 Pusat; 12,84 Selatan; 11,52 Timur;
10,10 Utara menunjukkan support tidak seragam. Kontribusi musiman terhadap ranking
belum diketahui. Tidak ada komposit seasonal baru atau data pengganti.

**Kriteria penerimaan:**

| Kriteria register | Bukti/status |
|---|---|
| Setiap scene/tanggal dan ekspor merekonstruksi periode/AOI | **BLOCKED**, belum ada scene/task/AOI historis atau replay berotorisasi |
| Hash raster terhubung ke ekspor aktual | Hash file aktual **PASS**; hubungan task historis **BLOCKED** |
| Support temporal serta batas surface-versus-air dinyatakan | Tahunan dan batas klaim **PASS**; bulanan **BLOCKED** |
| Tidak mengklaim scene 2024 terverifikasi dari metadata | **PASS**, semua sumber sekarang membedakan resep yang dimaksud dan asal historis |
| Recompute polygon/pixel dan efek input revisi | **PASS**, 140 nilai dan fixed-set local M1–M4 |

**Status keseluruhan: BLOCKED** secara eksternal; bagian lokal selesai.
**Outstanding dependency:** operator GEE yang berotorisasi atau arsip asli task,
scene dan versi AOI. **Keputusan lintas tim:** koordinator memilih pembatasan
estimand ke komposit pagi berlangit cerah versus klaim representasi tahunan yang
memerlukan komposit/sensitivity tambahan (TM-01). Rekomendasi: gunakan klaim
komposit yang terbatas dan mixed-period proxy framing; jangan menafsirkan limit
akses GEE sebagai bukti temporal stability. Agent 3 menilai ranking jika input
komposit/support baru mengubah hasil. Keputusan belum ditandatangani.

## DW-01 — Record supplementary Dynamic World scope and denominator semantics

**Severity:** P2. **Temuan asli:** semua fraksi kategorikal null, tidak diperlukan
persamaan M1–M4 tetapi masih diminta R3; kode `frac` memakai denominator valid label
sementara dokumentasi menyebut seluruh cell. Luas cell terkecil dibulatkan menjadi 0.

**Akar masalah:** raster label belum diekspor; conditional fraction exactextract
langsung disalin ke kolom whole-cell fraction. Pembulatan km² enam desimal
menghilangkan luas 0,42288454 m². Ini tidak terbukti mengubah skor baseline,
karena fraksi belum terisi dan model memakai luas master.

**Berkas diubah/ditambah:** `scripts/02b_aggregate_remote_sensing.py`,
`scripts/02c_dynamic_world_fractions_gee.js`, `scripts/02d_validate_remote_sensing.py`,
`tests/test_remote_sensing_grid.py`, `tests/test_remote_sensing_remediation.py`,
`docs/remote_sensing_deliverable_status.md`, metadata/handoff terkait dan
`data/processed/remote_sensing_remediated/remote_sensing_grid.{csv,gpkg,meta.json}`.

**Koreksi:**

1. R2 tetap COMPLETE untuk delivery numerik. R3 secara eksplisit PARTIAL dan
   supplementary untuk M1–M4; tidak ada categorical-area claim yang didukung.
   Deferral disarankan, belum dinyatakan resmi disetujui.
2. `*_fraction` kini C_k/A (kelas berlabel / seluruh luas poligon terpotong);
   `*_fraction_valid` C_k/V (kelas / support valid), support V/A dan missing share
   1−V/A terpisah. Sembilan kelas termasuk snow/ice direkonsiliasi. Tanpa support,
   fraksi kelas tetap null; tanpa seluruh ekspor label, support juga null.
3. Validasi raster label menolak CRS, resolusi, nodata, tipe atau kode kelas tidak
   sesuai. Skrip GEE memakai transform affine eksplisit dan tie mode eksplisit
   ke kode terkecil; perubahan ini adalah resep future export, belum hasil nyata.
4. `qa_area_m2` ditambahkan dan serialisasi luas mempertahankan 15 digit signifikan.
   CSV/GPKG revised konsisten dengan geometri. Pengukuran dan flags lama tidak diubah.
5. Output revised terpisah dari baseline. Kontrak urutan delapan kolom pertama,
   join `grid_id`, dan alias `lst_c`/`ndvi` tetap kompatibel dengan loader lokal jhim.

**Perintah uji:** perintah RS-01 di atas ditambah
`node --check scripts/02c_dynamic_world_fractions_gee.js`.
**Hasil:** 40 tests PASS, termasuk partial-valid-label fixture, fractional pixel
overlap, zero support, semua sembilan kelas, invalid code/nodata, round-trip luas
sub-m², loader jhim dan kesesuaian atribut/geometri CSV–GPKG. Fraksi kategori aktual
tetap null untuk 2.765 cell; probabilitas tetap tersedia untuk 2.764 cell dan tidak
diganti menjadi fraksi. Tidak ada source/output penelitian yang diganti data sintetis;
data sintetis hanya dipakai dalam fixture pengujian.

**Reproduksibilitas:** agregasi dijalankan dua kali ke direktori terpisah:
`data/processed/remote_sensing_remediated` dan
`outputs/qa/agent1_remediation/reproduction2`. CSV numerik/null identik, atribut
GPKG identik, semua geometri sama, metadata identik kecuali build timestamp.
Bukti `reproduction_equivalence.json`. Ini bukan fresh-environment integration
test IN-02; versi environment lokal dan `pip check` disimpan secara terpisah.

**Efek ilmiah sebelum/sesudah:** fixture half-support yang dahulu akan terbaca
tree/built 0,5/0,5 sekarang 0,25/0,25 dengan 0,5 unknown (conditional tetap
0,5/0,5). Untuk data nyata, 383 nilai `qa_area_km2` memiliki presisi lebih tinggi;
sel terkecil berubah 0 menjadi 4,22884536660195e-7 km². Ditambahkan 12 kolom
(42 total). Semua nilai pada 29 kolom lama lainnya identik. Tidak ada perubahan
score/rank M1–M4 pada fixed legacy comparison (bukti `rs_input_revision_model_effect.csv`).
Tidak ada estimasi efek fraksi kategorikal nyata karena raster label belum ada.

**Kriteria penerimaan:**

| Kriteria register | Bukti/status |
|---|---|
| Required LST/NDVI lane tetap complete | **PASS**, seluruh 2.765 ID numeric dan hash baseline terjaga |
| R3 partial/deferred atau ekspor aktual terverifikasi | Status PARTIAL **PASS**; formal deferral **PENDING**, ekspor tetap **BLOCKED** |
| Probabilitas tidak direlabel sebagai fractions | **PASS** |
| Denominator teruji dan luas positif memadai | **PASS** kode/fixture/luas aktual; actual categorical intersections **BLOCKED** sampai ekspor ada |

**Status keseluruhan: PARTIAL**. Koreksi teknis denominator dan luas selesai;
penutupan issue memerlukan coordinator-signed deferral beserta penghapusan klaim
kategorikal lintas proyek, atau hasil label nyata dan verifikasi tambahannya.
**Outstanding dependency:** keputusan scope, GEE hanya jika R3 tetap dipertahankan.
**Keputusan lintas tim:** disarankan defer R3 dari primary M1–M4, tanpa menyatakan
R3 COMPLETE. Keputusan itu belum diasumsikan disetujui dari hasil test.

## Dependensi lintas tim dan keputusan yang belum ditandatangani

**RS-02 / P1, Agent 3:** `rs_qa_policy_support.csv` memuat semua ID dan keanggotaan
kebijakan; `rs_temporal_support.csv` memuat area dan dukungan observasi. Target
JKT_R037_C062 dihitung independen: 6.724,131207485083 / 24.223,111369723836 m² =
0,277591557288115. Nilai LST 42,234 °C/NDVI 0,2961 tersampaikan. Pengecualian QA
bukan missing delivery. Baseline 0,5: 2.764 RS eligible / 2.538 route-present;
0,25 atau include-as-flagged: 2.765 / 2.539; strict rs_qa_ok: 2.752 / 2.527.
Kebijakan belum memperhitungkan koreksi dukungan demografi DM-01/DM-02. Threshold,
normalization, ranking/top-budget skenario dan alasan final tetap owner Agent 3.
Rekomendasi sementara mempertahankan baseline dengan label provisional dan
mempublikasikan alternatif relaxed/strict; persetujuan primary QA belum ada.

**TM-01:** periode deklaratif RS 2024 tidak menyamakan OSM 2026 dengan 2024.
Agent 1 memasok pembatasan thermal; perubahan dashboard dan klaim lintas proyek
menjadi owner terkait. Pilihan mixed-period exploratory study versus historical
inference tetap perlu persetujuan koordinator.

**MD-03:** masukkan relaxed/strict thermal-support policies sebagai family QA,
pisahkan perubahan eligible set dari perubahan input numerik. Seasonal-support
family tidak boleh diisi hasil buatan karena belum tersedia.

**IN-01/IN-02:** integrator dapat memilih proposed revised RS table secara eksplisit,
menggabungkan skrip dan nullable supplementary schema, serta menjalankan pipeline
dari frozen rasters sesuai `docs/remote_sensing_reproduction.md`. Tidak ada runtime
dependency sibling path di skrip baru. Lock environment lintas tim, candidate
commit, fresh environment dan consolidated tests belum dikerjakan Agent 1.

**QA-01:** auditor harus menilai bukti dan memperbarui acceptance/gates sendiri.
Tidak ada dokumen audit diubah. Tidak ada klaim project/paper siap rilis.

## Identitas baseline dan hasil revisi

| File | SHA256 |
|---|---|
| Baseline canonical RS CSV | `49297937f9510c13beceee986b2067dba05df7939800d9b7307852db9bec135a` |
| Baseline canonical RS GPKG | `26547bbe5486fafeec765ec5ca99394be70abb3d0d2f187dcf41490007663944` |
| Baseline canonical RS meta JSON | `a98974bbcc45251402006716a45aa429158abb650668937f0c0b03f466994267` |
| Frozen thermal GeoTIFF | `f46d0db14f2f667a533eff7960bb870b4b2676709af43e70d08e670a075958dd` |
| Frozen DW probability GeoTIFF | `c36b618e81c61568cc037c171f2bba44f542420a3ee46e446d38ff2af7de7037` |
| Revised RS CSV | `fb9937c760590931d0126b064437f2ac5b66ae089901b1184d8698cf4849dbf0` |

Daftar hash rinci source/input/output serta versi Python/package disimpan dalam
`docs/remote_sensing_export_manifest.json`. Hasil revisi siap untuk integrasi
terkendali sebagai perbaikan lokal; RS-01 tetap externally blocked dan DW-01
menunggu keputusan scope. Temuan penelitian final harus menunggu integrasi
dukungan sumber dari Agent 2, evaluasi ilmiah Agent 3 dan re-audit independen.
