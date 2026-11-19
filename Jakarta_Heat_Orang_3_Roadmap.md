# Roadmap Orang 3 — Data Scientist & Modeling Engineer

**Proyek:** Jakarta Heat Inequality Mapper  
**Fokus paper:** *Evaluating How Population Vulnerability and Walking Accessibility to Public Green Spaces Change Urban Heat Intervention Priorities in Jakarta*  
**PIC:** Orang 3  
**Status awal:** Orang 2 telah membagikan master grid Jakarta 500 m.

## Ringkasan job dan urutan

| Job | Pekerjaan | Kapan dimulai | Output wajib |
|---|---|---|---|
| **4A** | Setup Python + kesepakatan format data (*data contract*) | **Sekarang**, setelah menerima master grid | Environment aktif; grid terbaca; skema kolom disepakati |
| **4B** | Prototype dashboard Streamlit dengan **data dummy** | **Paralel** dengan pengolahan Landsat oleh Orang 1 dan WorldPop/OSM oleh Orang 2 | `dashboard/app.py` dapat dibuka |
| **6A** | Hitung dan bandingkan empat model prioritas panas | **Setelah** seluruh indikator asli tersedia | `priority_models.csv` |
| **6B** | Validasi ranking, autokorelasi spasial, dan sensitivitas | **Setelah** Job 6A | Tabel evaluasi + peta/hasil statistik |
| **6C** | Dashboard final dan hasil untuk paper | **Setelah** Job 6A–6B; UI dasarnya sudah ada dari Job 4B | Dashboard final + figur/tabel paper |

**Alur dependensi:** `Master Grid → (4A dan 4B paralel dengan Orang 1/2) → data gabungan → 6A → 6B → 6C`.

---

## Job 4A — Setup & Data Contract (kerjakan sekarang)

### Langkah 1 — Buat struktur folder

Buka terminal VS Code dari folder `jakarta-heat` dan siapkan struktur berikut:

```text
jakarta-heat/
├── .venv/
├── data/
│   └── processed/
│       ├── grid_500m_jakarta.gpkg
│       └── modeling/
├── scripts/
│   ├── 03_prepare_model.py
│   ├── 04_priority_model.py
│   └── 05_spatial_validation.py
├── dashboard/
│   └── app.py
└── outputs/
    ├── figures/
    └── tables/
```

PowerShell (jika folder belum ada):

```powershell
mkdir dashboard, outputs\figures, outputs\tables, data\processed\modeling -Force
```

### Langkah 2 — Aktivasi virtual environment dan instal dependensi

Jika sudah punya Python 3.12 dan `.venv`, **jangan install ulang Python**.

```powershell
.\.venv\Scripts\Activate.ps1
python --version
python -m pip install streamlit geopandas pandas numpy scikit-learn folium streamlit-folium scipy matplotlib libpysal esda
```

### Langkah 3 — Uji pembacaan master grid

Buat `scripts/03_prepare_model.py`:

```python
from pathlib import Path
import geopandas as gpd

root = Path(__file__).resolve().parents[1]
path = root / "data/processed/grid_500m_jakarta.gpkg"
grid = gpd.read_file(path)

assert "grid_id" in grid.columns, "Kolom grid_id tidak ada"
assert grid["grid_id"].notna().all(), "Ada grid_id kosong"
assert grid["grid_id"].is_unique, "Ada grid_id duplikat"
assert grid.crs is not None, "CRS grid tidak ada"

print("Jumlah grid:", len(grid))
print("CRS:", grid.crs)
print("Contoh kolom:", list(grid.columns))
print(grid[["grid_id"]].head())
```

Jalankan:

```powershell
python scripts/03_prepare_model.py
```

**Lulus Job 4A** jika grid bisa dibaca, CRS terdeteksi, `grid_id` tidak kosong, dan tidak ada duplikat.

### Langkah 4 — Sepakati skema file antaranggota

Semua CSV harus memuat `grid_id` yang sama dengan master grid; **satu baris per grid**.

| Kolom | Sumber/PIC | Pengertian |
|---|---|---|
| `grid_id` | Master grid / Orang 2 | Kunci penggabungan unik |
| `lst_c` | Orang 1 | Rata-rata/median LST dalam °C per grid (catat jenis statistiknya) |
| `ndvi` | Orang 1 | Ringkasan NDVI per grid |
| `population` | Orang 2 | Estimasi total penduduk per grid |
| `pop_child` | Orang 2 | Estimasi penduduk usia 0–14 tahun |
| `pop_elderly` | Orang 2 | Estimasi penduduk usia 65+ |
| `park_distance_m` | Orang 2 | Jarak melalui jaringan jalan kaki ke taman publik terdekat, dalam meter |
| `park_access_500m` | Orang 2 | 1 jika taman dapat dijangkau ≤500 m, selain itu 0 |

**Format penyerahan yang disarankan:**

- Orang 1 → `data/processed/remote_sensing_grid.csv` (`grid_id,lst_c,ndvi`).
- Orang 2 → `data/processed/population_accessibility_grid.csv` (`grid_id,population,pop_child,pop_elderly,park_distance_m,park_access_500m`).
- Orang 3 → `data/processed/modeling/merged_grid.csv` setelah *join* dan validasi.

Jangan menganggap `0` dan nilai kosong sama; data yang tidak tersedia ditulis sebagai *missing/NaN*.

---

## Job 4B — Prototype Dashboard (paralel dengan Orang 1 & 2)

### Langkah 1 — Buat dashboard sederhana

Buat `dashboard/app.py`:

```python
from pathlib import Path
import geopandas as gpd
import numpy as np
import streamlit as st

st.set_page_config(page_title="Jakarta Heat Inequality", layout="wide")
st.title("Jakarta Heat Inequality Mapper")
st.warning("DEMO: Skor pada tampilan ini masih data dummy, bukan hasil penelitian.")

root = Path(__file__).resolve().parents[1]
grid = gpd.read_file(root / "data/processed/grid_500m_jakarta.gpkg")

rng = np.random.default_rng(42)
grid["dummy_score"] = rng.random(len(grid))

st.metric("Jumlah grid", f"{len(grid):,}")
st.write("Preview atribut master grid")
st.dataframe(grid.drop(columns="geometry").head(20))

# Tampilkan titik tengah grid sebagai prototype ringan.
points = grid.to_crs("EPSG:32748").copy()
points["geometry"] = points.geometry.representative_point()
points = points.to_crs("EPSG:4326")
points["lat"] = points.geometry.y
points["lon"] = points.geometry.x
st.map(points[["lat", "lon", "dummy_score"]], latitude="lat", longitude="lon")
```

### Langkah 2 — Jalankan aplikasi

```powershell
python -m streamlit run dashboard/app.py
```

Buka alamat lokal yang diberikan Streamlit (umumnya `http://localhost:8501`). Pastikan jumlah grid, contoh atribut, dan titik grid Jakarta muncul.

### Langkah 3 — Siapkan rancangan fitur dashboard akhir

- Pemilihan model prioritas: **M1, M2, M3, M4**.
- Peta sebaran skor dan 10% grid dengan prioritas tertinggi.
- Ringkasan jumlah penduduk di grid prioritas.
- Perubahan peringkat suatu grid antar-model.
- Grafik perbandingan dan uji sensitivitas.

**Lulus Job 4B** jika aplikasi dapat dibuka tanpa data asli. Tulisan **DEMO/data dummy** wajib tetap terlihat sampai data asli terpasang.

---

## Job 6A — Comparative Heat Priority Modeling (tunggu data asli)

### Langkah 1 — Terima dan gabungkan data

Pastikan ketiga file tersedia: master grid, CSV Orang 1, dan CSV Orang 2.

1. Baca CSV menggunakan `pandas.read_csv()`.
2. Pastikan `grid_id` unik pada masing-masing file.
3. Gabungkan dengan `merge(..., on="grid_id", how="left", validate="one_to_one")`.
4. Hitung persentase *missing values* dan periksa rentang LST, NDVI, serta estimasi populasi.
5. Simpan ke `data/processed/modeling/merged_grid.csv`.

**Jangan** membuat nilai LST/populasi yang hilang menjadi nol. Tetapkan terlebih dahulu aturan penanganan *missing* dan laporkan jumlah grid yang dikeluarkan dari perbandingan.

### Langkah 2 — Bangun empat model pembanding

| Model | Variabel |
|---|---|
| **M1** | LST saja |
| **M2** | LST + NDVI (NDVI rendah → prioritas lebih tinggi) |
| **M3** | LST + NDVI + total populasi |
| **M4** | LST + NDVI + paparan kelompok usia + aksesibilitas taman |

**Prinsip:** gunakan normalisasi yang konsisten, arah skor yang sama (tinggi = lebih prioritas), dan bobot yang ditetapkan **sebelum** melihat hasil. Jika membandingkan M3 dengan M4, jelaskan apakah total populasi tetap masuk M4 dan bagaimana mencegah *double counting* populasi usia rentan.

Contoh normalisasi min–max:

```python
def minmax(series):
    vmin, vmax = series.min(), series.max()
    if vmax == vmin:
        return series * 0
    return (series - vmin) / (vmax - vmin)
```

Untuk variabel seperti NDVI dan akses taman, balik arah jika perlu (misalnya `1 - minmax(ndvi)`). Untuk *park_distance_m*, tangani jarak tak-terjangkau secara eksplisit—jangan sembarang memberi nilai ekstrem.

### Langkah 3 — Hasilkan skor dan ranking

Simpan `data/processed/modeling/priority_models.csv` dengan kolom minimal:

```text
grid_id,m1_score,m1_rank,m2_score,m2_rank,m3_score,m3_rank,m4_score,m4_rank
```

Gunakan aturan peringkat yang sama di semua model; misalnya rank 1 = prioritas tertinggi. Bandingkan seluruh model pada **set grid valid yang sama** agar perbandingan tidak bias.

---

## Job 6B — Spatial Statistics & Robustness (setelah 6A)

### Langkah 1 — Bandingkan keputusan model

- **Spearman correlation:** mengukur kesamaan urutan ranking antar-model.
- **Jaccard Index:** mengukur irisan 10% grid berprioritas tertinggi antar-model.
- **Perubahan ranking:** hitung `m1_rank - m4_rank` untuk melihat wilayah yang naik/turun prioritas.
- **Cakupan penduduk:** jumlahkan populasi pada 10% grid teratas di tiap model.

Simpan metrik ke `outputs/tables/model_comparison.csv`.

### Langkah 2 — Uji pola spasial

1. Gabungkan skor M4 ke geometri master grid melalui `grid_id`.
2. Gunakan `libpysal` untuk mendefinisikan tetangga spasial (misalnya **Queen contiguity**).
3. Hitung **Global Moran's I** untuk menguji autokorelasi spasial.
4. Jika memungkinkan, hitung **Local Moran/LISA** untuk memetakan klaster tinggi–tinggi dan rendah–rendah.
5. Laporkan pilihan matriks bobot, *p-value*, dan keterbatasan pengujian berganda.

Simpan hasil peta ke `outputs/figures/` dan statistik ke `outputs/tables/`.

### Langkah 3 — Sensitivity analysis

Uji beberapa konfigurasi yang masuk akal:

- Bobot masing-masing indikator ±10–20% kemudian normalisasi ulang.
- Ambang akses taman 500 m vs. 1.000 m (**butuh data jarak mentah**, bukan hanya kolom biner).
- Jika waktu cukup, coba ukuran grid alternatif (misalnya 250 m atau 1 km) dan ulang agregasi data sumber.

Bandingkan seberapa stabil 10% grid prioritas tertinggi di seluruh skenario. Jangan menyebut hasilnya *robust* sebelum ada bukti metrik yang mendukung.

---

## Job 6C — Dashboard Final & Kebutuhan Paper

1. Ganti semua data dummy di dashboard dengan `priority_models.csv` dan tabel indikator asli.
2. Tampilkan peta choropleth grid 500 m untuk M1–M4.
3. Tambahkan filter model, grafik ranking, dan tabel 10% grid prioritas tertinggi.
4. Tambahkan perbandingan metrik (Spearman, Jaccard, cakupan populasi) serta peta LISA jika tersedia.
5. Ekspor gambar berkualitas publikasi (PNG/SVG) dan tabel CSV untuk bagian *Results* paper.
6. Cantumkan sumber data, tahun, keterbatasan LST (bukan suhu udara), keterbatasan OSM, dan asumsi bobot.

**Output akhir Orang 3:**

```text
data/processed/modeling/merged_grid.csv
data/processed/modeling/priority_models.csv
outputs/tables/model_comparison.csv
outputs/figures/*.png
dashboard/app.py
```

---

## Checklist penyelesaian

- [ ] **4A:** Grid terbaca; `grid_id` unik; kolom dan format CSV disepakati.
- [ ] **4B:** Streamlit menyala dengan data dummy berlabel DEMO.
- [ ] **6A:** Dataset asli tergabung; tidak ada *join* yang menggandakan grid; empat model dan ranking tersedia.
- [ ] **6B:** Spearman, Jaccard, Moran's I, dan minimal satu uji sensitivitas terdokumentasi.
- [ ] **6C:** Dashboard memakai data asli; visualisasi dan tabel paper diekspor.

## Prioritas tindakan sekarang

**Kerjakan Job 4A → 4B lebih dulu.** Keduanya bisa dilakukan sekarang tanpa menunggu Orang 1 dan 2. Setelah kedua rekan selesai menyediakan variabel penelitian, lanjutkan **Job 6A → 6B → 6C** secara berurutan.
