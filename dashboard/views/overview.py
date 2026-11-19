import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from lib import ui  # noqa: E402
from lib.context import C, get_ctx  # noqa: E402

ctx = get_ctx()
st.title("Jakarta Heat Inequality Mapper")
ui.banner(ctx)

st.markdown(
    "**Pertanyaan penelitian.** Apakah memasukkan jumlah penduduk, kelompok usia rentan, dan aksesibilitas "
    "berjalan kaki (hasil model) ke taman secara material mengubah lingkungan Jakarta yang diprioritaskan "
    "untuk mitigasi panas perkotaan, dibandingkan peta prioritas yang hanya berbasis panas?\n\n"
    "Kerangka ini adalah **indeks prioritas relatif** untuk membandingkan keputusan penentuan prioritas. "
    "Ini **bukan** model risiko kesehatan dan bukan estimasi hubungan kausal."
)

c1, c2, c3, c4 = st.columns(4)
f = ctx.feat
c1.metric("Grid 500 m (master)", f"{ctx.status.n_grid:,}")
if f is not None:
    c2.metric("Total penduduk (WorldPop)", f"{f['population'].sum():,.0f}")
    c3.metric("Grid valid data Person 2", f"{int(f['valid_p2'].sum()):,}")
    c4.metric("Grid valid untuk M1–M4", f"{int(f['valid'].sum()):,}")

st.subheader("Area dan unit analisis")
st.markdown(
    "- Lima kota administratif daratan DKI Jakarta (Jakarta Pusat, Utara, Barat, Selatan, Timur); "
    "Kepulauan Seribu tidak termasuk.\n"
    "- Periode campuran: termal/demografi 2024; proksi jaringan dan taman kandidat OSM 19 November 2026. "
    "Unit: grid 500 m × 500 m (EPSG:32748), dipotong batas daratan; sel tepi/pantai "
    "dapat jauh lebih kecil dari 0,25 km² (lihat `coverage_ratio`).\n"
    "- Kunci penggabungan: `grid_id` (satu baris per grid; tidak ada grid yang dihapus diam-diam)."
)

st.subheader("Status masukan")
rows = [{"masukan": k, "ada": "ya" if v["exists"] else "belum", "path": v["path"]} for k, v in ctx.status.files.items()]
st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
for n in ctx.status.notes:
    st.caption(n)
from jhim.pipeline import official_outputs_status  # noqa: E402

off = official_outputs_status(ctx.paths)
if not off["exists"]:
    st.caption("Keluaran resmi (data/processed/modeling, outputs/tables) belum dibuat; dashboard menghitung langsung "
               "dari masukan dengan kode yang sama (`jhim`).")
elif off["stale_inputs"]:
    st.warning(f"Keluaran resmi dibuat {off['built_at']} tetapi masukan berikut sudah berubah sejak itu: "
               f"{', '.join(off['stale_inputs'])}. Jalankan ulang `python scripts/run_agent3_pipeline.py`.")
else:
    st.caption(f"Keluaran tersimpan dibuat {off['built_at']}; kode, konfigurasi, masukan, dan isi keluaran cocok. "
               "Ini verifikasi reproduksi perangkat lunak, bukan pengesahan ilmiah.")

st.subheader("Empat model pembanding (bobot PROVISIONAL)")
comp = {"M1": "LST", "M2": "LST, NDVI", "M3": "LST, NDVI, populasi", "M4": "LST, NDVI, anak + lansia, jarak taman"}
st.dataframe(pd.DataFrame([{"model": m, "komponen": comp[m], "rumus": C.MODEL_FORMULAS[m]} for m in C.MODELS]),
             hide_index=True, width="stretch")
st.caption(C.WEIGHTS_STATUS + " n(·) = min-max setelah dipotong persentil 5–95 pada himpunan grid valid bersama.")

st.subheader("Sumber data")
st.markdown(
    "| Variabel | Sumber | Pemilik |\n|---|---|---|\n"
    "| LST (°C), NDVI | Landsat 9 C2 L2, median komposit 2024 (GEE) | Agent 1 |\n"
    "| Probabilitas pohon/bangunan | Dynamic World V1, median 2024 | Agent 1 |\n"
    "| Penduduk total, 0–14, 65+ | WorldPop (estimasi, bukan sensus) | Person 2 |\n"
    "| Taman, jaringan jalan kaki | OpenStreetMap; jarak jaringan hasil model | Person 2 |\n"
)

st.subheader("Keterbatasan utama")
st.markdown(
    "- **LST ≠ suhu udara.** LST adalah suhu permukaan dari satelit pada jam lintas Landsat (±10.00 WIB), median tahunan.\n"
    "- Penduduk WorldPop adalah estimasi pemodelan; kelompok usia diturunkan dari proporsi.\n"
    "- Jarak taman adalah jarak jaringan **hasil model** dari titik representatif grid ke titik representatif "
    "poligon taman OSM, bukan pintu masuk terverifikasi; status akses publik taman tidak diverifikasi.\n"
    "- 226 grid tanpa rute terhitung **bukan** berarti tidak ada taman; ditangani dengan kebijakan eksplisit dan sensitivitas.\n"
    "- Bobot model belum disepakati tim; semua hasil harus dibaca bersama uji sensitivitas."
)
