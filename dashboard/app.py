"""Jakarta Heat Inequality Mapper — dashboard riset (Person 3 / Agent 3).

Jalankan dari akar repositori:
    python -m streamlit run dashboard/app.py

Mode "Data asli" membaca data/processed/ (Person 2 + remote_sensing_grid.csv Agent 1 bila ada).
Mode "DEMO" membaca data/processed/dummy/ (data sintetis berlabel) dan selalu menampilkan peringatan.
Prototipe Job 4B yang asli dipertahankan di dashboard/app_4b_prototype.py.
"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.context import MODE_DEMO, MODE_REAL  # noqa: E402

VIEWS = Path(__file__).resolve().parent / "views"

st.set_page_config(page_title="Jakarta Heat Inequality Mapper", page_icon=":material/thermostat:", layout="wide")

with st.sidebar:
    st.markdown("### Jakarta Heat Inequality Mapper")
    st.radio("Sumber data", [MODE_REAL, MODE_DEMO], key="mode",
             help="DEMO memakai data sintetis untuk menguji tampilan; bukan hasil penelitian.")
    st.selectbox(
        "Jarak taman tidak terhitung (226 grid pada data asli)",
        ["exclude", "worst", "median"], key="unreachable",
        format_func={"exclude": "Keluarkan dari perbandingan (baseline)",
                     "worst": "Sensitivitas: defisit maksimum",
                     "median": "Sensitivitas: median teramati"}.get,
        help="park_distance_m kosong berarti rute TIDAK dihitung — bukan jarak 0, bukan tak terhingga, "
             "dan bukan bukti tidak ada taman publik. Pilihan selain baseline adalah skenario sensitivitas.",
    )
    st.caption("Unit: grid 500 m (2.765 sel), lima kota daratan DKI Jakarta. LST/demografi 2024; OSM 19 November 2026. "
               "LST = suhu permukaan tanah dari satelit, bukan suhu udara.")

pages = [
    st.Page(VIEWS / "overview.py", title="Ikhtisar", icon=":material/home:", default=True),
    st.Page(VIEWS / "data_explorer.py", title="Penjelajah data", icon=":material/map:"),
    st.Page(VIEWS / "heat_vegetation.py", title="Panas dan vegetasi", icon=":material/thermostat:"),
    st.Page(VIEWS / "priority_models.py", title="Model prioritas", icon=":material/leaderboard:"),
    st.Page(VIEWS / "model_comparison.py", title="Perbandingan model", icon=":material/compare_arrows:"),
    st.Page(VIEWS / "spatial_stats.py", title="Statistik spasial", icon=":material/grid_on:"),
    st.Page(VIEWS / "sensitivity.py", title="Robustness / sensitivitas", icon=":material/tune:"),
    st.Page(VIEWS / "methods.py", title="Metode dan keterbatasan", icon=":material/menu_book:"),
]
st.navigation(pages).run()
