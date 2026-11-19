import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from lib import maps, ui  # noqa: E402
from lib.context import D, get_ctx  # noqa: E402

ctx = get_ctx()
st.title("Penjelajah data")
ui.banner(ctx)
f = ctx.feat
if f is None:
    st.stop()

LAYERS = {
    "Penduduk total (jiwa per grid)": ("population", "Blues", 0, "jiwa"),
    "Kepadatan penduduk (jiwa/km² daratan)": ("pop_density_km2", "Blues", 0, "jiwa/km²"),
    "Anak 0–14 (jiwa)": ("pop_child", "Purples", 0, "jiwa"),
    "Lansia 65+ (jiwa)": ("pop_elderly", "Purples", 0, "jiwa"),
    "Penduduk rentan 0–14 + 65+ (jiwa)": ("pop_vulnerable", "Purples", 0, "jiwa"),
    "Porsi penduduk rentan": ("vuln_share", "Purples", 3, "0–1"),
    "Jarak jaringan ke taman terdekat (m)": ("park_distance_m", "Greens_r", 0, "m"),
    "Jarak snap titik grid ke jaringan (m)": ("grid_snap_m", "Greys", 0, "m"),
    "Coverage sel di daratan (0–1)": ("coverage_ratio", "Greys", 3, "0–1"),
}

st.subheader("Peta grid 500 m")
c1, c2 = st.columns([2, 1])
layer = c1.selectbox("Variabel", list(LAYERS))
col, cmap, digits, unit = LAYERS[layer]
scale = c2.radio("Skala warna", ["Nilai (dipotong persentil 2–98)", "Nilai penuh"], horizontal=False)
v = pd.to_numeric(f[col], errors="coerce")
lo, hi = (v.quantile(0.02), v.quantile(0.98)) if scale.startswith("Nilai (") else (v.min(), v.max())

if col == "park_distance_m":
    st.caption("Abu-abu = **rute tidak dihitung** (226 grid pada data asli). Ini bukan jarak 0 m, bukan jarak tak "
               "hingga, dan bukan bukti tidak ada taman publik. Akses publik taman OSM tidak diverifikasi.")
maps.choropleth(ctx, f, col, layer, cmap, lo, hi, extra=("kota", "population", "park_distance_m", "grid_snap_m"),
                missing_label="tidak tersedia / rute tidak dihitung" if col == "park_distance_m" else "tidak tersedia",
                digits=digits)

c1, c2 = st.columns(2)
with c1:
    ui.histogram(v, f"{layer}")
with c2:
    st.markdown("**Ringkasan**")
    st.dataframe(v.describe().to_frame("nilai").T.round(3), width="stretch")
    st.caption(f"Kosong: {int(v.isna().sum()):,} grid. Nilai 0: {int((v == 0).sum()):,} grid.")

st.subheader("Akses taman (biner, dari jarak jaringan model)")
acc = f.assign(
    akses=np.select(
        [f["f_park_route_missing"], f["park_distance_m"] <= 500, f["park_distance_m"] <= 1000],
        ["rute tidak dihitung", "≤ 500 m", "500–1000 m"], default="> 1000 m"))
colors = {"≤ 500 m": "#1a9850", "500–1000 m": "#91cf60", "> 1000 m": "#fc8d59", "rute tidak dihitung": "#7b3294"}
maps.categorical(ctx, acc, "akses", colors, "Akses taman", extra=("kota", "park_distance_m", "grid_snap_m"))
st.caption("Kategori ungu ditampilkan terpisah agar grid tanpa rute tidak tercampur dengan jarak jauh yang teramati.")

st.subheader("Diagnostik kualitas data")
st.dataframe(D.quality_table(f), hide_index=True, width="stretch")
g = f.assign(kota=f["kota"].fillna("(tanpa kota)")).groupby("kota")
kota = pd.DataFrame({
    "n_grid": g.size(), "populasi": g["population"].sum().round(0),
    "% rentan": (100 * g["pop_vulnerable"].sum() / g["population"].sum()).round(1),
    "rute tidak dihitung": g["f_park_route_missing"].sum(),
    "jarak median (m)": g["park_distance_m"].median().round(0),
    "% grid ≤500 m": (100 * g["park_access_500m"].mean()).round(1),
    "snap > 250 m": g["f_snap_far"].sum(), "coverage < 10%": g["f_low_coverage"].sum(),
}).reset_index()
st.dataframe(kota, hide_index=True, width="stretch")
ui.download(kota, "ringkasan_kota_person2", ctx)

st.markdown("**Grid yang ditandai QA**")
flags = {"f_park_route_missing": "rute taman tidak dihitung", "f_snap_far": "snap > 250 m",
         "f_low_coverage": "coverage < 10%", "f_pop_zero": "populasi = 0"}
if "qa_age_source_no_support" in f:
    flags["qa_age_source_no_support"] = "dukungan sumber usia tidak tersedia"
if "qa_population_source_no_support" in f:
    flags["qa_population_source_no_support"] = "dukungan sumber populasi tidak tersedia"
pick = st.multiselect("Tampilkan grid dengan bendera", list(flags), default=list(flags), format_func=flags.get)
sel = f.loc[f[pick].any(axis=1)] if pick else f.iloc[0:0]
cols = list(dict.fromkeys(["grid_id", "kota", "population", "pop_vulnerable", "park_distance_m", "grid_snap_m", "coverage_ratio",
        "raw_population", "raw_pop_child", "raw_pop_elderly", "support_version", "eligibility_reasons", *pick]))
st.dataframe(sel[[c for c in cols if c in sel.columns]], hide_index=True, width="stretch", height=280)
st.caption(f"{len(sel):,} grid. Daftar ini untuk ditinjau Person 2 saat QA final (R7).")
ui.download(sel[[c for c in cols if c in sel.columns]], "grid_qa_person2", ctx)
