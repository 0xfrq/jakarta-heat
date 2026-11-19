# Metode analisis Person 3 / Agent 3

Halaman **Metode dan keterbatasan** merender dokumen ini. Parameter ada di `jhim/config.py`;
keputusan audit dan alternatif ada di `docs/research_decisions.md` dan `docs/spatial_inference_spec.md`.

**Lingkup periode campuran:** LST/NDVI dan demografi merujuk 2024; jaringan dan taman kandidat OSM
diekstrak 19 November 2026. Ini penyaringan eksploratif lima kota daratan, bukan akses publik 2024
terverifikasi, perubahan temporal, paparan individu, atau validasi hasil kesehatan/kebijakan.
Status pengiriman data lengkap berbeda dari dukungan sumber, QA ilmiah, dan kelayakan analisis.
Koreksi audit disimpan terpisah dari baseline; kebijakan utama belum disahkan tim.

> **Status:** bobot, ambang, dan kelas prioritas berstatus **PROVISIONAL**. Nilai ini ditetapkan
> Person 3 sebelum data LST asli tersedia, tidak diturunkan dari literatur tertentu, dan **belum
> disepakati tim**. Uji sensitivitas wajib dilaporkan bersama setiap hasil.

## 1. Data dan kontrak

| Berkas | Pemilik | Kolom wajib | Kolom opsional dipakai |
|---|---|---|---|
| `data/processed/grid_500m_jakarta.gpkg` | Person 2 | `grid_id`, geometri (EPSG:32748) | `kota`, `area_km2`, `coverage_ratio` |
| `data/processed/grid_master.csv` | Person 2 | `grid_id` | `kota`, `area_km2`, `coverage_ratio` |
| `data/processed/spatial_features.csv` | Person 2 | `grid_id`, `population`, `pop_child`, `pop_elderly`, `park_distance_m` | `park_reachable`, `park_access_500m`, `park_access_1000m`, `grid_snap_m` |
| `data/processed/remote_sensing_grid.csv` | Agent 1 | `grid_id`, `lst_c`, `ndvi` | `lst_valid_frac` (alias `lst_valid_fraction`), `lst_unc_k` (`lst_unc_mean_k`), `lst_obs` (`lst_observation_count`), `trees_prob` (`tree_prob_mean`), `built_prob` (`built_prob_mean`), `rs_qa_ok`, `rs_qa_flags` |

Pada keluaran Agent 1 (commit `cdda424`, `scripts/02b_aggregate_remote_sensing.py`), `lst_c` = rata-rata
tertimbang cakupan piksel (exactextract) dari **median per-piksel** LST 2024 dalam tiap poligon grid
terpotong; `ndvi` analog. `rs_qa_ok = False` (13 grid: 12 ketidakpastian ST_QA > 5 K, 1 cakupan LST
parsial) ditandai `f_rs_qa`; grid dengan porsi piksel LST valid < 0,5 (1 grid) dikeluarkan. Fraksi kelas
Dynamic World masih kosong (BLOCKED di sisi Agent 1), sehingga hanya probabilitas pohon yang dipakai,
dan hanya di skenario sensitivitas.

Aturan kontrak:

- `grid_id` adalah satu-satunya kunci; satu baris per grid; ID kosong atau duplikat menghentikan proses.
- Penggabungan selalu *left join* satu-ke-satu ke master grid; urutan dan jumlah baris (2.765) dijaga.
  Baris di luar master diabaikan dan dilaporkan; grid master tanpa baris menjadi kosong, **tidak pernah 0**.
- Teks bukan angka di kolom numerik adalah galat struktur, bukan NaN diam-diam.
- Berkas bertanda `is_dummy=1` ditolak di folder data asli.
- Satuan: LST °C (suhu **permukaan**), NDVI −1…1, penduduk dalam jiwa per grid, jarak dalam meter
  jaringan jalan kaki, `area_km2` luas daratan sel, `coverage_ratio` = `area_km2` / 0,25.

Status masukan (`jhim.data.assess_inputs`): `INVALID`, `P2_ONLY` (remote sensing belum ada),
`RS_INCOMPLETE` (ada grid tanpa nilai LST/NDVI yang dikirim), `COMPLETE` (pengiriman, bukan kelayakan QA).

## 2. Pembersihan dan kelayakan

| Bendera | Arti | Dampak baseline |
|---|---|---|
| `f_<var>_missing`, `f_<var>_range` | nilai kosong / di luar rentang (LST 15–60 °C, NDVI −1…1, penduduk ≥ 0) | nilai di luar rentang dikosongkan; grid tidak layak |
| `f_park_route_missing` | `park_distance_m` kosong = **rute tidak dihitung** | dikeluarkan dari himpunan bersama (kebijakan `exclude`) |
| `f_park_imputed` | jarak diisi skenario `worst`/`median` | hanya di skenario sensitivitas |
| `f_reach_mismatch` | `park_reachable` tidak konsisten dengan ada/tidaknya jarak | dilaporkan |
| `f_park_access_500m_mismatch`, `..._1000m_...` | flag biner tidak cocok dengan jarak | dilaporkan |
| `f_snap_far` | `grid_snap_m` > 250 m | ditandai untuk QA; sensitivitas mengeluarkan |
| `f_low_coverage` | `coverage_ratio` < 0,10 (sel pantai/batas) | ditandai; sensitivitas mengeluarkan |
| `f_pop_zero` | populasi = 0 | tetap layak (komponen populasi = minimum) |
| `f_age_gt_pop` | anak + lansia > 105% populasi + 1 | tidak layak |
| `f_lst_low_valid` | `lst_valid_frac` < 0,5 (bila kolom ada) | tidak layak |

Dukungan sumber versi DM-01 dipertahankan saat ingestion. `qa_age_source_no_support` atau
`qa_population_source_no_support` mengosongkan nilai analitis yang bersangkutan; ekspor asli ada pada
`raw_population`, `raw_pop_child`, `raw_pop_elderly`. Nol dengan dukungan valid berbeda dari NoData.
Porsi usia undefined untuk populasi nol/kosong; skenario komposisi mengeluarkan denominator tersebut.
`eligibility_reasons` mencatat sebab yang dapat bertumpang tindih. Loader lama tanpa support masih
kompatibel tetapi menampilkan peringatan bahwa dukungan belum terintegrasi, bukan kepastian nol.

Kelayakan: `elig_m1` (LST), `elig_m2` (+NDVI), `elig_m3` (+populasi), `elig_m4` (+anak, lansia, jarak
yang dipakai). **`valid = elig_m4` adalah himpunan grid pembanding bersama untuk SEMUA model**, sehingga
korelasi dan overlap antar-model tidak pernah dihitung pada subset grid yang berbeda. Dampak pilihan ini
terhadap model panas murni dilaporkan oleh `eligibility_effect_m1.csv` (berapa grid top-M1 yang hilang
karena dikeluarkan).

### Jarak taman yang tidak terhitung

`park_distance_m` kosong **tidak** berarti grid menempel taman, jarak 0, jarak tak hingga, atau tidak ada
taman publik. Nilai mentah tidak pernah diubah. Model memakai `park_distance_used_m`:

- `exclude` (**baseline**): tetap kosong → grid dikeluarkan dari perbandingan.
- `worst` (sensitivitas): diisi 1.000 m → defisit maksimum (asumsi terburuk).
- `median` (sensitivitas): diisi median jarak teramati (asumsi netral).

Pada data asli, 226 grid (8,2%) tanpa rute memuat ±463 ribu penduduk dan sebagian besar bukan sel tepi
(median `coverage_ratio` = 1,0); karena itu kebijakan ini diperiksa di uji sensitivitas, bukan dianggap sepele.

## 3. Model M1–M4

Notasi: `n(x)` = min-max setelah dipotong pada persentil 5 dan 95, dihitung **pada himpunan grid valid
bersama**, hasil 0–1. Semua komponen berarah sama: tinggi = lebih prioritas.

| Komponen | Rumus | Arah / alasan |
|---|---|---|
| `lst` | `n(lst_c)` | permukaan lebih panas → prioritas lebih tinggi |
| `ndvi_low` | `1 − n(ndvi)` | vegetasi lebih sedikit → prioritas lebih tinggi |
| `pop` | `n(log1p(population))` | jumlah orang terpapar; `log1p` mencegah grid sangat padat mendominasi |
| `vuln` | `n(log1p(pop_child + pop_elderly))` | jumlah penduduk usia rentan (0–14, 65+) |
| `park_deficit` | `min(jarak, 1000) / 1000` | 0 m → 0, ≥ 1 km → 1; skala absolut, tidak dinormalisasi ulang |

| Model | Rumus (bobot PROVISIONAL) |
|---|---|
| M1 | `S1 = n(LST)` |
| M2 | `S2 = 0,60 n(LST) + 0,40 [1 − n(NDVI)]` |
| M3 | `S3 = 0,40 n(LST) + 0,30 [1 − n(NDVI)] + 0,30 n(log1p(populasi))` |
| M4 | `S4 = 0,30 n(LST) + 0,20 [1 − n(NDVI)] + 0,25 n(log1p(anak + lansia)) + 0,25 min(jarak, 1000)/1000` |

- **Peringkat:** 1 = prioritas tertinggi. Pemotongan persentil membuat beberapa grid jenuh di skor 1,0;
  seri dipecah oleh skor dengan min-max murni (tanpa pemotongan), lalu `grid_id` (naik). Hasilnya
  deterministik dan tidak bergantung urutan baris.
- **Prioritas tinggi:** `ceil(0,10 × n_valid)` grid teratas. Ambang 5% dan 20% dilaporkan sebagai pembanding.
- **Kelas (PROVISIONAL):** top 10% / 10–25% / 25–50% / 50–100% dari grid valid, berbasis peringkat.
- **Populasi jumlah vs kepadatan:** baseline memakai jumlah (orang yang terpapar per grid). Kepadatan
  (`population / area_km2`) menjadi skenario sensitivitas karena sel pantai yang sangat kecil dapat
  berkepadatan tinggi dengan jumlah penduduk kecil.
- **Double counting:** M4 tidak memuat total populasi. Namun pada data Person 2, korelasi Spearman antara
  komponen `pop` dan `vuln` = **0,999** (`outputs/qa/agent3/person2_component_spearman.csv`): jumlah anak +
  lansia praktis proporsional terhadap total penduduk (porsi rentan ±29–30% di semua kota). Konsekuensinya,
  perbedaan M3 → M4 terutama digerakkan oleh akses taman dan bobot, **bukan** oleh komposisi usia.
  Skenario "porsi rentan (bukan jumlah)" menguji alternatif komposisi; porsi rentan sendiri hampir tidak
  berpola spasial (Moran's I ≈ 0,07–0,11).
- Skor adalah **indeks prioritas relatif** dalam himpunan grid yang sama, bukan model risiko kesehatan
  dan bukan klaim kausal.

## 4. Perbandingan model (`jhim/compare.py`)

Semua metrik pada himpunan valid bersama (fungsi menolak bila ada skor kosong di grid valid):
Spearman ρ dan Kendall τ-b antar skor; Jaccard dan porsi retensi himpunan top 5/10/20%; ringkasan
perpindahan peringkat absolut (rata-rata, median, p90, maks, % berpindah > 10% n); matriks transisi kelas;
ringkasan distribusi skor; sebaran grid top per kota; profil grid "tetap top / masuk / keluar" M1 → M4;
efek kelayakan untuk M1.

## 5. Statistik spasial (`jhim/spatial.py`)

- **Bobot baseline: Queen contiguity** pada poligon grid, distandardisasi baris. Alasan: grid reguler
  500 m; Queen (≤ 8 tetangga) memperlakukan tetangga diagonal sebagai bersebelahan, simetris, dan mudah
  dijelaskan. Implementasi STRtree (`intersects`) teruji identik dengan `libpysal.weights.Queen` pada
  master grid (20.988 pasangan) dan ~1000× lebih cepat. Queen poligon berbeda dari Queen lattice
  (`R###_C###`) pada 205 sel tepi yang terpotong; poligon dipilih karena mengikuti daratan sebenarnya.
- **Sensitivitas bobot:** Rook (≤ 4) dan KNN-8 (centroid).
- **Islands:** grid tanpa tetangga dikeluarkan dari uji, dilaporkan, lalu bobot dibangun ulang. Grid
  penuh tidak punya island; subset (mis. jarak taman tanpa rute) dapat menimbulkan 1–2 island.
- **Inferensi:** permutasi bersyarat 999 kali, seed 42 (p minimum = 0,001). LISA dilaporkan dua kali:
  `klaster_p05` (tanpa koreksi), `klaster_fdr` (Benjamini–Hochberg q = 0,05) dan BY konservatif.
  Global memakai hipotesis autokorelasi positif dengan p permutasi ekor atas; LISA conditional memakai
  `alternative="directed"` eksplisit sebagai pembanding lama, serta sensitivitas two-sided dan 9.999
  permutasi. Family usulan adalah satu peta terpilih, semua grid layak tanpa island. Pilihan tail/family
  belum disahkan. BH membutuhkan asumsi dependensi; label bukan validasi indeks atau risiko kesehatan.
- Klaster LISA adalah pola deskriptif, bukan penjelasan kausal; hasil bergantung pada definisi tetangga dan
  unit 500 m (MAUP).

## 6. Sensitivitas (`jhim/sensitivity.py`)

Eksploratif, *one-at-a-time* (setiap skenario mengubah tepat satu keputusan; diuji otomatis). Untuk M2,
M3, M4 bila komponennya relevan:

| Kelompok | Skenario |
|---|---|
| bobot | tiap komponen ×0,8 dan ×1,2 (dinormalisasi ulang); bobot sama rata |
| normalisasi | min-max murni; persentil 1–99; peringkat persentil |
| ambang taman | biner > 500 m, > 1000 m; batas jenuh 750 m, 1500 m |
| jarak taman kosong | `worst`, `median` (himpunan grid bertambah; dilaporkan) |
| penduduk | kepadatan alih-alih jumlah (M3); porsi rentan alih-alih jumlah, total populasi alih-alih rentan (M4) |
| tutupan lahan | Dynamic World `1 − trees_prob` menggantikan NDVI (hanya bila kolom tersedia) |
| eksklusi QA | keluarkan snap > 250 m; keluarkan coverage < 10% |

Metrik: Jaccard top 5/10/20% terhadap baseline, Spearman pada irisan grid, jumlah grid top yang berubah,
grid tambahan yang masuk top. Per grid: porsi skenario (yang membuat grid itu layak) di mana grid tetap
top 10% (`stable_share`); "stabil" = ≥ 80%. Laporkan stabilitas **dan** ketidakstabilan; jangan menyebut
hasil "robust" tanpa angka pendukung. Frekuensi skenario bukan probabilitas atau interval kepercayaan.
Ringkasan one-at-a-time tidak mencakup semua definisi akses. Registry audit terpisah mencakup skenario
gabungan 16 kombinasi serta keluarga tujuan/pintu masuk/hambatan yang belum tersedia; keluarga yang
blocked tidak dihitung sebagai bukti stabilitas. Perbandingan fixed-intersection dan universe berubah
disimpan terpisah, bersama seluruh anggota dan denominator.

## 7. Keterbatasan

- LST adalah suhu permukaan dari Landsat 9 (median komposit 2024, jam lintas pagi), bukan suhu udara,
  bukan paparan panas individu; resolusi termal asli lebih kasar dari 30 m.
- WorldPop adalah estimasi pemodelan; kelompok usia diturunkan dari proporsi.
- Jarak taman adalah jarak jaringan **model** dari titik representatif grid ke titik representatif poligon
  taman OSM (bukan pintu masuk terverifikasi); status akses publik, jam buka, dan kualitas taman tidak
  diverifikasi; kelengkapan OSM bervariasi.
- 226 grid tanpa rute dan 66 grid dengan snap > 250 m perlu ditinjau Person 2 (R7).
- Bobot belum disepakati; hasil peringkat sensitif terhadap pilihan normalisasi dan ambang (lihat §6).
- Grid 500 m dan pemotongan batas daratan memengaruhi statistik spasial (MAUP, efek tepi).

## 8. Reproduksibilitas

- Satu perintah: `python scripts/run_agent3_pipeline.py` (kode keluar 2 bila remote sensing belum ada).
- Setiap run menulis manifest versi 2: hash SHA-256 masukan termasuk support/fallback, konfigurasi,
  kode aktif, parameter runtime aktual, versi paket/lock, commit dan isi keluaran. Perubahan salah satu
  membuat keluaran usang. Manifest lama belum membuktikan kecocokan ilmiah. GPKG byte hash konservatif
  dibedakan dari ekuivalensi geometri/numerik. Kandidat audit memakai direktori keluaran terpisah.
- Seed permutasi tetap (42); peringkat deterministik; tes otomatis di `tests/agent3/`.
