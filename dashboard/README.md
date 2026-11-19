# Dashboard dan pipeline analisis — Person 3 / Agent 3

Jakarta Heat Inequality Mapper: membandingkan peta prioritas mitigasi panas berbasis LST saja (M1)
dengan kerangka yang menambahkan vegetasi (M2), penduduk (M3), serta penduduk usia rentan dan akses
berjalan kaki ke taman kandidat (M4). Grid 500 m, 2.765 sel, lima kota daratan DKI Jakarta.
Periode campuran: termal/demografi 2024; proksi OSM 19 November 2026. Dukungan demografi dan
keputusan ilmiah belum final; lihat `docs/research_decisions.md` dan `handoff/REMEDIATION_AGENT3.md`.

Metode lengkap: [`docs/agent3_methods.md`](../docs/agent3_methods.md). Serah terima:
[`handoff/AGENT3_HANDOFF.md`](../handoff/AGENT3_HANDOFF.md).

## Struktur

```text
jhim/                      logika ilmiah (tanpa Streamlit; dapat diuji)
  config.py                SEMUA parameter: kolom, rentang, bobot M1-M4, ambang, seed, jalur
  data.py                  baca + validasi + gabung + bersihkan; status masukan
  models.py                komponen, normalisasi, skor, peringkat, kelas
  compare.py               Spearman, Kendall, Jaccard, transisi, kota, efek kelayakan
  spatial.py               bobot Queen/Rook/KNN, islands, Moran global, LISA + FDR
  sensitivity.py           skenario one-at-a-time
  figures.py               figur matplotlib (paper)
  pipeline.py              orkestrasi, manifest provenance, diagnostik Person 2
dashboard/
  app.py                   entry point Streamlit (navigasi + sidebar)
  app_4b_prototype.py      prototipe Job 4B asli (dipertahankan)
  lib/                     cache data, peta pydeck (EPSG:4326), elemen UI
  views/                   8 halaman
scripts/run_agent3_pipeline.py   satu perintah untuk semua langkah
scripts/03_..07_*.py             langkah terpisah (pembungkus jhim.pipeline; kompatibel dengan roadmap)
tests/agent3/                    pytest (fixture sintetis + data repo bila ada)
```

## Perintah (Windows PowerShell, dari akar repositori)

```powershell
# 1. environment (sekali)
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r dashboard\requirements.txt

# 2. tes
python -m pytest tests\agent3 -q

# 3. status masukan
python scripts\run_agent3_pipeline.py --status

# 4a. sebelum remote sensing tersedia: diagnostik data Person 2 -> outputs\qa\agent3\
python scripts\run_agent3_pipeline.py --p2-only

# 4b. setelah data\processed\remote_sensing_grid.csv tersedia: pipeline lengkap
python scripts\run_agent3_pipeline.py
#     sensitivitas kebijakan jarak taman kosong untuk seluruh pipeline (opsional):
python scripts\run_agent3_pipeline.py --unreachable worst

# 5. dashboard (http://localhost:8501)
python -m streamlit run dashboard\app.py

# latihan dengan data sintetis (keluaran ke folder demo, berwatermark)
python scripts\run_agent3_pipeline.py --demo
```

Kode keluar pipeline: `0` sukses, `2` masukan hulu belum tersedia (bukan galat kode), `1` galat data.

## Halaman dashboard

| Halaman | Data asli tanpa remote sensing | Dengan remote sensing |
|---|---|---|
| Ikhtisar | pertanyaan, area, status masukan, model, sumber, keterbatasan | + status keluaran resmi |
| Penjelajah data | peta penduduk, anak, lansia, porsi rentan, kepadatan, jarak taman, kategori akses, QA | sama |
| Panas dan vegetasi | status "belum tersedia", metadata & pratinjau raster Agent 1, kontrak kolom | peta/histogram LST, NDVI, Dynamic World, QA cakupan |
| Model prioritas | definisi + status "belum tersedia" | peta skor/kelas/top-N, bobot eksploratif berlabel, tabel top |
| Perbandingan model | status "belum tersedia" | Spearman, Kendall, Jaccard, perpindahan, transisi, peta, kota |
| Statistik spasial | Moran/LISA variabel Person 2 | + skor M1–M4, LST, NDVI |
| Robustness / sensitivitas | daftar skenario | ringkasan skenario, peta stabilitas |
| Metode dan keterbatasan | `docs/agent3_methods.md` + konfigurasi aktif | sama |

Mode **DEMO** (sidebar) memakai `data/processed/dummy/` (sintetis, `is_dummy=1`) dan selalu
menampilkan banner merah "MODE DEMO — DATA SINTETIS". Tidak ada nilai dummy yang tampil di mode data asli.

## Keluaran

| Lokasi | Isi | Kapan ditulis |
|---|---|---|
| `outputs/qa/agent3/` | diagnostik deskriptif data Person 2 (kualitas, ringkasan kota, korelasi komponen, Moran/LISA jarak taman, daftar grid QA) | `--p2-only` |
| `data/processed/modeling/` | `merged_grid.csv` (fitur tervalidasi + bendera), `priority_models.csv`, LISA, stabilitas, `rank_shift_m1_m4.csv`, `run_manifest.json` | pipeline lengkap, data asli |
| `outputs/tables/` | perbandingan, overlap, transisi, kota, Moran, sensitivitas, top-10% per model | pipeline lengkap |
| `outputs/figures/` | PNG/SVG 300 dpi | pipeline lengkap |
| `outputs/gis/priority_models.gpkg` | grid + atribut model (EPSG:32748) | pipeline lengkap |
| `data/processed/modeling_demo/`, `outputs/demo/` | keluaran latihan dari data dummy | `--demo` |

`data/processed/modeling_demo/` dan `outputs/demo/` yang sudah ada di Git dibuat oleh versi kode Person 3
sebelumnya (format lama); jalankan ulang `--demo` bila ingin memperbaruinya. Semuanya sintetis.

## Kamus kolom `merged_grid.csv` (ringkas)

`grid_id`, `lst_c`, `ndvi`, opsional RS (`lst_valid_frac`, `lst_unc_k`, `lst_obs`, `trees_prob`, `built_prob`),
`population`, `pop_child`, `pop_elderly`, `park_distance_m` (mentah), `park_distance_used_m` (setelah
kebijakan), `park_reachable`, `park_access_500m`, `park_access_1000m`, `grid_snap_m`, `kota`, `area_km2`,
`coverage_ratio`, turunan `pop_vulnerable`, `vuln_share`, `pop_density_km2`, bendera `f_*` (lihat metode §2),
kelayakan `valid_rs`, `valid_p2`, `elig_m1..elig_m4`, `valid`.

`priority_models.csv`: `grid_id`, `valid`, komponen `c_lst`, `c_ndvi_low`, `c_pop`, `c_vuln`, `c_park`,
dan per model `m#_score` (0–1), `m#_rank` (1 = tertinggi), `m#_top` (top 10%), `m#_class`.
