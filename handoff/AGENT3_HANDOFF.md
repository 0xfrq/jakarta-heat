# AGENT 3 HANDOFF — Modeling, Spatial Statistics, Dashboard

> **Pembaruan 20 November 2026:** Bagian bertanggal 19 November di bawah adalah riwayat baseline,
> bukan status ilmiah final. Remediasi audit telah menghasilkan kandidat terpisah n=2526 (baseline
> audited n=2538 dipertahankan), dukungan sumber/null, attribution/ablations, skenario dan inferensi
> eksplisit, serta koreksi lingkup dashboard. **Ledger final (20 Nov 2026, agen pengganti):
> `handoff/REMEDIATION_AGENT3.md`** — suite 116 passed/1 skipped, replay dua-run PASS
> (`outputs/remediation/qa/replay_verification.json`), verifikasi independen PASS, browser 8 halaman + 6 interaksi.
> Kesembilan isu berstatus PARTIAL/BLOCKED pada dependensi A1/A2/koordinator; tidak ada klaim penutupan auditor.
> Belum ada commit/merge, persetujuan metode, kandidat terintegrasi, atau independent re-audit. Jangan menafsirkan
> status "pipeline ready", angka n=2538/top 254, maupun "PASS" historis di bawah sebagai status terkini,
> paper-ready, atau temuan auditor tertutup.

- Branch / worktree: `agent/person3` di `D:\jakarta-heat-agent3`, basis commit `f9b5c02`. **Belum di-commit**
  (sesuai aturan: commit hanya atas instruksi).
- Tanggal: 2026-11-19. Python 3.12.10, pandas 3.1.1, geopandas 1.2.0, libpysal 4.15.1, esda 2.10.0, streamlit 1.67.0.
- Masukan empiris: Person 2 `data/processed/spatial_features.csv` + Agent 1
  `D:\jakarta-heat-agent1\data\processed\remote_sensing_grid.csv` (commit Agent 1 `cdda424`, dibaca saja
  via `JHIM_RS_PATH`; tidak disalin dan tidak diubah).
- **Status akhir: PIPELINE READY + HASIL EMPIRIS AWAL TERSEDIA (provisional, menunggu QA R7 dan
  kesepakatan bobot).** Rinciannya ada di §15.

---

## 1. Status awal pekerjaan Person 3 (audit sebelum perubahan)

Bukti: semua file dibaca; skrip dijalankan pada salinan data di folder sementara (`JHIM_ROOT=<tmp>`)
memakai `D:\jakarta-heat\.venv` (tanpa streamlit, libpysal, esda, pytest).

| Komponen | File | Klasifikasi awal | Bukti |
|---|---|---|---|
| Konfigurasi terpusat | `jhim/config.py` | IMPLEMENTED BUT NOT VERIFIED | bobot M1–M4 ada, tanpa sumber/keputusan tim, tanpa tes |
| Loader master grid | `jhim/data.py::read_grid_gdf` | IMPLEMENTED BUT NOT VERIFIED | `03_prepare_model.py` lulus 4A (2.765 grid, EPSG:32748) |
| Loader Person 2 | `jhim/data.py::load_population_inputs` | **BROKEN** (data asli) | tidak membaca `spatial_features.csv`; mencari `park_access_grid.csv` → `DataError: kolom yang masih kurang: ['park_distance_m','park_access_500m']` |
| Loader remote sensing | `jhim/data.py` | BLOCKED BY UNAVAILABLE INPUTS | `remote_sensing_grid.csv` belum ada saat audit |
| Pembersihan + bendera | `jhim/data.py::clean_values` | PARTIAL | tanpa bendera snap/coverage/park_reachable; opsi `cap` menimpa jarak mentah |
| Model M1–M4 | `jhim/models.py` | IMPLEMENTED BUT NOT VERIFIED | jalan di dummy, tanpa tes |
| Perbandingan | `jhim/compare.py` | PARTIAL | Spearman, Jaccard, rank shift; tanpa Kendall/kelas/transisi/kota |
| Moran/LISA | `jhim/spatial.py` | IMPLEMENTED BUT NOT VERIFIED (gagal runtime) | `ImportError: Pasang dulu: python -m pip install libpysal esda` |
| Sensitivitas | `jhim/sensitivity.py` | PARTIAL | bobot, ambang biner, normalisasi; tanpa skenario jarak kosong/penduduk/QA |
| Figur | `jhim/figures.py`, `scripts/07_export_paper.py` | IMPLEMENTED BUT NOT VERIFIED | 9 figur demo tercipta |
| Data dummy | `jhim/dummy.py`, `scripts/00_make_dummy_inputs.py`, `data/processed/dummy/` | COMPLETE (sintetis) | `is_dummy=1`, folder terpisah |
| Hasil demo terkomit | `data/processed/modeling_demo/`, `outputs/demo/` | sintetis | `"source": "dummy"` |
| Dashboard | `dashboard/app.py` | PARTIAL (prototipe 4B) | docstring menyebut dirinya `app_4b_prototype.py`; hanya populasi; "dashboard final" yang dirujuk tidak ada |
| Skrip duplikat | `script/03_prepare_model.py`, `script/04_priority_model.py` | DEAD CODE | isi identik, salinan contoh roadmap (dibiarkan) |
| Tes Person 3 | — | NOT IMPLEMENTED | hanya `tests/test_walking_pipeline.py` (milik Person 2) |

## 2. File asli utama dan fungsinya

`jhim/` (paket logika tanpa Streamlit: config, data, models, compare, spatial, sensitivity, figures, io, util, dummy),
`scripts/00,03–07` (langkah Job 4A–6C), `dashboard/app.py` (prototipe 4B), `Jakarta_Heat_Orang_3_Roadmap.md`
(rencana kerja dan kontrak kolom awal). Arsitektur ini **dipertahankan**; semua perluasan dibangun di atasnya.

## 3. Bug yang diperbaiki

| # | Bug | Perbaikan | Bukti |
|---|---|---|---|
| 1 | Loader Person 2 tidak membaca `spatial_features.csv` | urutan baca: `spatial_features.csv` → format gabungan lama → berkas terpisah | `test_real_person2_known_counts` |
| 2 | `cap` menimpa `park_distance_m` mentah | jarak mentah tak pernah diubah; imputasi ke `park_distance_used_m` + bendera | `test_raw_distance_never_overwritten` |
| 3 | Moran/LISA tidak jalan | dependensi terpasang; `requirements.txt` | `test_spatial.py` |
| 4 | Islands hanya dihitung | dikeluarkan, dilaporkan, bobot dibangun ulang | `test_islands_are_dropped_and_reported`; data asli: 1 island (Queen) pada jarak taman |
| 5 | Queen libpysal 61 detik di master grid | Queen STRtree, **identik** (20.988 pasangan), 0,05 detik | `test_fast_queen_matches_libpysal_and_lattice` |
| 6 | Dashboard final tidak ada | 8 halaman, prototipe dipindah ke `app_4b_prototype.py` (riwayat Git terjaga) | `test_dashboard_app.py`, screenshot |
| 7 | Teks bukan angka menjadi NaN diam-diam | galat struktur | `test_non_numeric_values_are_structural_errors` |
| 8 | Skenario Dynamic World gagal pada data asli (1 grid tanpa `tree_prob_mean`) | skenario mendeklarasikan kolom wajib; grid dikeluarkan dari skenario itu dan dilaporkan | `test_scenario_specific_missing_values_are_excluded_and_reported` |
| 9 | Nama kolom opsional Agent 1 tidak dikenali | alias bermakna identik (`lst_valid_fraction`, `lst_unc_mean_k`, `lst_observation_count`, `tree_prob_mean`, `built_prob_mean`), `rs_qa_ok` teks | `test_agent1_column_names_accepted` |
| 10 | Peta: "lain" vs "tidak dipakai" sulit dibedakan; histogram dashboard kosong | arsir/tanpa isian; `mark_rect` | diverifikasi visual |

## 4. File yang dibuat atau diubah

- Diubah: `jhim/{config,data,models,compare,spatial,sensitivity,figures,io,util}.py`, `scripts/03–07_*.py`
  (kini pembungkus tipis `jhim.pipeline`; perintah lama tetap berlaku), `README.md` (bagian penunjuk di akhir).
- Dipindah: `dashboard/app.py` → `dashboard/app_4b_prototype.py`.
- Baru: `jhim/pipeline.py`, `scripts/run_agent3_pipeline.py`, `dashboard/{app.py, README.md, requirements.txt}`,
  `dashboard/lib/{__init__,context,maps,ui}.py`, `dashboard/views/*.py` (8), `tests/agent3/*.py` (9 berkas),
  `docs/agent3_methods.md`, `.streamlit/config.toml` (bind `localhost`, telemetri mati), dokumen ini.
- Keluaran yang dihasilkan (tidak di-commit): `data/processed/modeling/*`, `outputs/tables/*` (29),
  `outputs/figures/*` (26), `outputs/gis/priority_models.gpkg`, `outputs/qa/agent3/*`.
- **Tidak disentuh:** data Person 2, skrip Person 2 (`01,02,03_format,04_extract,05_walking,05a,06_merge,07–09`),
  semua file Agent 1, `data/processed/dummy/`, `modeling_demo/`, `outputs/demo/`.

## 5. Rumus model dan asumsi

Detail lengkap: `docs/agent3_methods.md` §3. Ringkas (bobot **PROVISIONAL**):

- `n(x)` = min-max setelah potong persentil 5–95 **pada himpunan grid valid bersama**.
- M1 `n(LST)`; M2 `0,60 n(LST) + 0,40 [1−n(NDVI)]`; M3 `0,40 n(LST) + 0,30 [1−n(NDVI)] + 0,30 n(log1p pop)`;
  M4 `0,30 n(LST) + 0,20 [1−n(NDVI)] + 0,25 n(log1p(anak+lansia)) + 0,25 min(jarak,1000)/1000`.
- Peringkat 1 = tertinggi; seri dipecah skor min-max murni lalu `grid_id`. Top = `ceil(0,10·n)`.
  Kelas: 10/25/50/100%.
- Himpunan bersama `valid` = LST + NDVI + penduduk + jarak taman (kebijakan `exclude`) + konsistensi usia.
- Jarak kosong: `exclude` (baseline), `worst`, `median` (sensitivitas). Snap > 250 m dan coverage < 10%
  ditandai, tidak dikeluarkan di baseline.

## 6. Halaman dashboard yang berfungsi

Ikhtisar, Penjelajah data, Panas dan vegetasi, Model prioritas (termasuk bobot eksploratif berlabel),
Perbandingan model, Statistik spasial, Robustness/sensitivitas, Metode dan keterbatasan. Semua 8 halaman
diverifikasi tanpa exception dalam tiga kondisi:

1. data asli tanpa RS (halaman model menampilkan status "belum tersedia", tanpa angka pengganti);
2. data asli + RS Agent 1 (`JHIM_RS_PATH`);
3. DEMO (banner merah "MODE DEMO — DATA SINTETIS" di setiap halaman).

Peta pydeck memakai GeoJSON EPSG:4326 hasil proyeksi dari EPSG:32748. Verifikasi visual dilakukan dengan
Edge headless (Playwright, `channel=msedge`) — 0 exception, 0 error konsol. Angka di dashboard identik
dengan keluaran pipeline (mis. M4 top: 254 grid, 1.533.525 penduduk).

## 7. Metode statistik dan parameter

- Perbandingan: Spearman, Kendall τ-b, Jaccard top 5/10/20%, retensi, perpindahan peringkat absolut,
  matriks transisi kelas, ringkasan kota, profil "masuk/keluar top", efek kelayakan M1. Semua dihitung
  pada himpunan bersama; fungsi menolak bila himpunan grid antar-model berbeda.
- Spasial: Queen poligon (baseline, baris-standar), Rook dan KNN-8 sebagai sensitivitas; islands
  dikeluarkan dan dilaporkan; 999 permutasi, seed 42; LISA dengan p < 0,05 dan FDR-BH (q = 0,05); klaim memakai FDR.

## 8. Implementasi sensitivitas

`jhim/sensitivity.py`: eksploratif, *one-at-a-time* (diuji: tiap skenario mengubah tepat satu keputusan).
Kelompok skenario: bobot ±20% dan sama rata; normalisasi (min-max murni, 1–99, peringkat); ambang taman
(biner 500/1000, jenuh 750/1500); jarak kosong (`worst`, `median`); penduduk (kepadatan; porsi rentan;
total vs rentan); Dynamic World menggantikan NDVI; eksklusi QA (snap, coverage, `rs_qa_ok`). Metrik:
Jaccard top 5/10/20%, Spearman pada irisan, grid tambah/hilang, `stable_share` per grid.

## 9. Tes dan hasil verifikasi aktual

| Perintah | Hasil |
|---|---|
| `.venv\Scripts\python -m pytest tests\agent3 -q` | **91 passed** (233 detik) |
| `D:\jakarta-heat\.venv\Scripts\python -m unittest discover -s tests` (tes Person 2) | **Ran 10 tests, OK** |
| `python scripts\run_agent3_pipeline.py --status` (tanpa RS) | `P2_ONLY`, exit 0 |
| `python scripts\run_agent3_pipeline.py` (tanpa RS) | exit **2** "TERTUNDA", tidak ada keluaran resmi |
| `python scripts\run_agent3_pipeline.py --p2-only` | exit 0, 21 detik |
| `JHIM_RS_PATH=<agent1> python scripts\run_agent3_pipeline.py` | exit 0, ±91 detik, dua run identik (deterministik) |
| skrip 03→07 `--demo` berurutan (folder sementara) | semuanya exit 0 |
| AppTest 8 halaman × 2 mode + screenshot Edge | 0 exception, 0 error konsol |

Cakupan tes: skema, berkas hilang, ID duplikat/kosong/format Excel, tipe tidak terduga, join 1:1 dan urutan,
CRS dan proyeksi web, status masukan (4 kondisi), dummy di folder asli; normalisasi, arah skor, bobot,
determinisme terhadap pengacakan baris, pemecah seri, kelas; 226 jarak kosong vs jarak 0 sejati, kebijakan
imputasi, bendera snap, ketidakkonsistenan flag akses; matematika Spearman/Kendall/Jaccard/transisi,
penolakan himpunan campuran; Queen/Rook/KNN/lattice, islands, determinisme permutasi, tanda Moran,
FDR ⊆ p<0,05; skenario sensitivitas; pipeline end-to-end, manifest, deteksi masukan usang, kode keluar CLI;
navigasi dashboard dan fallback tanpa RS. Tes data asli Person 2 dan Agent 1 dilewati otomatis bila file tidak ada.

## 10. Hasil yang dihasilkan dari data asli

> **Status: hasil empiris AWAL.** Masukan asli dan tervalidasi oleh masing-masing pemilik (Person 2:
> validasi awal; Agent 1: 46 cek, 0 gagal kritis), tetapi **belum** melewati integrasi/QA final Person 2 (R7),
> dan bobot model masih PROVISIONAL. Jangan dikutip sebagai temuan final sebelum R7 dan kesepakatan bobot.
> Sumber: `outputs/tables/`, `outputs/qa/agent3/`, manifest `data/processed/modeling/run_manifest.json`
> (RS sha256 `49297937f9510c13…`).

**Kelayakan.** Status masukan `COMPLETE`: Agent 1 memberi LST/NDVI untuk semua 2.765 grid. Grid valid
bersama 2.538 (91,8%) = 2.765 − 226 tanpa rute taman − 1 grid yang dikeluarkan aturan QA
(`JKT_R037_C062`, sel tepi Jakarta Timur, `lst_valid_fraction` 0,28 < 0,5; Agent 1 menandainya `partial_lst`).
Catatan: versi awal kode memberi status `RS_INCOMPLETE` untuk kasus ini; sejak perbaikan, `RS_INCOMPLETE`
hanya berarti ada grid tanpa nilai dari Agent 1, sedangkan eksklusi QA dilaporkan sebagai catatan. 13 grid `rs_qa_ok=False` hanya ditandai. Efek kelayakan: 18 dari 277 grid
top-10% M1 (dihitung pada semua 2.764 grid ber-LST) berada di luar himpunan bersama, semuanya karena rute
taman tidak dihitung.

**Kesamaan peringkat (n = 2.538).**

| Pasangan | Spearman | Kendall τ-b | Jaccard top 10% | top M1 dipertahankan | rerata \|Δ peringkat\| |
|---|---|---|---|---|---|
| M1–M2 | 0,936 | 0,782 | 0,568 | 72% | 200 |
| M1–M3 | 0,906 | 0,737 | 0,481 | 65% | 235 |
| M1–M4 | 0,847 | 0,658 | **0,388** | **56% (142/254)** | 308 |
| M3–M4 | 0,897 | 0,735 | 0,411 | 58% | 268 |

Jaccard M1–M4 pada top 5% = 0,316; pada top 20% = 0,492. Sebanyak 48% grid berpindah > 10% n (254 posisi) dari M1 ke M4.

**Sebaran per kota (jumlah grid top 10%, M1 → M4).** Barat 39 → 63, Pusat 2 → 17, Selatan 48 → 32,
Timur 88 → 88, Utara 77 → 54.

**Profil grid top.** Penduduk di grid top: M1 13,0% → M3 15,4% → M4 14,6% dari penduduk grid valid.
Jarak taman median grid top M4 = 1.150 m dan **100% grid top M4 berjarak > 500 m** (M1: 86,6%). Grid yang
masuk top di M4 (112) rata-rata LST 43,4 °C vs yang keluar (112) 44,7 °C.

**Autokorelasi spasial.** Semua skor dan variabel berautokorelasi positif kuat di ketiga definisi
tetangga (Queen: I = 0,67 M1, 0,66 M2, 0,67 M3, 0,59 M4; LST 0,67; NDVI 0,64; semua p_sim = 0,001).
LISA M4 (FDR): 363 HH, 251 LL, 9 HL, 14 LH, 1.900 tidak signifikan. Variabel Person 2: log penduduk
I = 0,50, jarak taman I = 0,74, porsi rentan I = 0,07.

**Sensitivitas (top 10%).** Median Jaccard terhadap baseline: M2 0,93, M3 0,93, M4 0,90. Grid top yang
stabil (≥ 80% skenario): M2 91%, M3 93%, **M4 79%**. M4 paling sensitif terhadap:
- definisi rentan sebagai **porsi** alih-alih jumlah (Jaccard 0,35);
- akses taman **biner** 500/1000 m (0,53);
- batas jenuh 750/1500 m (0,64–0,68);
- normalisasi (0,74–0,81).

Sebaliknya M4 stabil terhadap bobot ±20% (≥ 0,86), eksklusi QA (≥ 0,96), dan perlakuan jarak kosong
(0,91; 11–13 dari 226 grid tambahan masuk top).

**Redundansi.** Spearman komponen `pop`–`vuln` = 0,999. Penggantian `vuln` dengan total populasi hampir
tidak mengubah M4 (Jaccard 0,98). Jadi efek M4 berasal dari jarak taman, bukan komposisi usia.

**Interpretasi yang dapat dipertahankan (sementara).** Pada data 2024 ini, menambahkan penduduk dan
aksesibilitas taman **mengubah secara material** himpunan grid prioritas dibanding peta panas saja
(hanya 56% top M1 tetap di top M4; pergeseran ke Jakarta Barat/Pusat, menjauh dari Utara/Selatan).
Perubahan itu terutama didorong oleh komponen jarak taman, dan besarnya bergantung pada spesifikasi
komponen taman serta definisi kerentanan. Ini indeks prioritas relatif, bukan risiko kesehatan.

## 11. Fitur yang belum tervalidasi karena data hulu

- Fraksi kelas Dynamic World (`tree_fraction`, dll.) kosong di sisi Agent 1 (BLOCKED: `jakarta_2024_dw_label_mode.tif`);
  dashboard/pipeline siap memakai probabilitas pohon dan akan menerima fraksi bila kontrak disepakati.
- Hasil §10 belum melewati QA geografis final Person 2 (R7).
- Remote sensing belum berada di lokasi kanonik `data/processed/remote_sensing_grid.csv` repo utama.

## 12. Ketergantungan pada Agent 1

Kontrak wajib `grid_id, lst_c, ndvi` (dipenuhi oleh `cdda424`); opsional sesuai `docs/agent3_methods.md` §1.
Bila Agent 1 memperbarui berkasnya, hash di manifest berubah dan halaman Ikhtisar menandai keluaran usang;
jalankan ulang pipeline. Agent 3 tidak mengubah skrip atau data Agent 1.

## 13. Perintah untuk Person 2 saat integrasi (PowerShell, dari akar repo)

```powershell
# environment (venv yang sudah ada cukup ditambah paketnya)
.\.venv\Scripts\Activate.ps1
python -m pip install -r dashboard\requirements.txt

# letakkan remote sensing Agent 1 di lokasi kanonik (setelah merge branch agent/person1), lalu:
python scripts\run_agent3_pipeline.py --status        # harus COMPLETE (catatan: 1 grid dikeluarkan QA, JKT_R037_C062)
python -m pytest tests\agent3 -q                       # harus 91 passed (atau lebih)
python scripts\run_agent3_pipeline.py                  # keluaran resmi + manifest
python scripts\run_agent3_pipeline.py --p2-only        # diagnostik Person 2 terbaru
python -m streamlit run dashboard\app.py               # http://localhost:8501

# alternatif tanpa menyalin berkas Agent 1:
$env:JHIM_RS_PATH = "D:\jakarta-heat-agent1\data\processed\remote_sensing_grid.csv"
python scripts\run_agent3_pipeline.py
python -m streamlit run dashboard\app.py
```

### Checklist QA final Person 2 (R7)

- [ ] 2.765 `grid_id` master identik di grid, `spatial_features.csv`, dan `remote_sensing_grid.csv` (`--status`).
- [ ] Inspeksi keselarasan spasial raster Agent 1 vs grid/demografi (QGIS: `outputs/gis/priority_models.gpkg`).
- [ ] Tinjau 226 grid tanpa rute dan 66 grid snap > 250 m (`outputs/qa/agent3/person2_flagged_grids.csv`,
      halaman Penjelajah data); putuskan apakah rute perlu dihitung ulang.
- [ ] Verifikasi interpretasi akses taman: titik representatif, bukan pintu masuk; status publik OSM.
- [ ] Tinjau sel pantai/batas (65 coverage < 10%; 101 `edge_cell` Agent 1) dan 13 grid `rs_qa_ok=False`.
- [ ] Pastikan peta model final mencerminkan masukan tervalidasi (Ikhtisar: "masih cocok dengan hash masukan").
- [ ] Jalankan ulang pipeline setelah koreksi QA; bandingkan `outputs/tables/model_comparison.csv`.

## 14. Keputusan metodologis yang masih terbuka (perlu tim)

1. **Bobot M2–M4** (provisional) dan apakah dipra-registrasi sebelum hasil final.
2. **Spesifikasi akses taman** (kontinu 1 km vs biner vs batas lain); M4 paling sensitif di sini.
3. **Definisi kerentanan**: jumlah anak + lansia (≈ total penduduk) vs porsi vs indeks lain.
4. Kebijakan 226 grid tanpa rute untuk hasil final (baseline `exclude` vs hitung ulang rute).
5. Normalisasi (potong 5–95 vs peringkat); 127 grid M1 jenuh di skor 1,0 (urutan oleh pemecah seri).
6. Ambang prioritas (10%) dan kelas; apakah memakai unit areal alternatif (250 m / 1 km) untuk MAUP.
7. Apakah grid `rs_qa_ok=False` (ketidakpastian ST_QA > 5 K) dikeluarkan di baseline.

## 15. Penilaian kesiapan akhir

| Aspek | Status | Bukti |
|---|---|---|
| Audit & pelestarian pekerjaan Person 3 | DONE | §1, `app_4b_prototype.py`, paket `jhim` dipertahankan |
| Lapisan data dan kontrak | DONE | 4 status, tes kontrak, data asli lolos |
| M1–M4, perbandingan, spasial, sensitivitas | DONE (software) | 91 tes, pipeline asli exit 0 |
| Dashboard 8 halaman | DONE | AppTest + screenshot 3 kondisi |
| Keluaran reproduksibel + provenance | DONE | manifest hash, run deterministik |
| Hasil empiris | **TERSEDIA, PROVISIONAL** | §10; menunggu R7 + kesepakatan bobot |

**Kesimpulan: PIPELINE READY; HASIL EMPIRIS AWAL TERSEDIA tetapi BELUM FINAL.** Temuan dunia nyata
belum boleh ditandai DONE sampai QA R7 Person 2 dan keputusan §14 selesai, lalu pipeline dijalankan ulang.
