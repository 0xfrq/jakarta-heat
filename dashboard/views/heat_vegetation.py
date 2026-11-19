import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from lib import REPO, maps, ui  # noqa: E402
from lib.context import C, get_ctx  # noqa: E402

ctx = get_ctx()
st.title("Panas dan vegetasi")
ui.banner(ctx)
st.caption("LST = **suhu permukaan tanah** (Landsat 9 ST_B10, median komposit 2024, jam lintas pagi), "
           "bukan suhu udara dan bukan rata-rata harian.")
f = ctx.feat
has_rs = f is not None and f["lst_c"].notna().any()

if not has_rs:
    ui.pending("Statistik LST/NDVI per grid")
    st.subheader("Yang sudah ada dari Agent 1 (raster, belum diagregasi ke grid)")
    rs_dir = REPO / "data/processed/remote_sensing"
    for tif in ("jakarta_2024_lst_ndvi_qa.tif", "jakarta_2024_trees_built_probability.tif"):
        p = rs_dir / tif
        st.markdown(f"- `{p.relative_to(REPO)}` — {'ada' if p.exists() else 'tidak ada'}")
    for name in ("landsat_metadata.json", "dynamic_world_metadata.json"):
        p = REPO / "docs" / name
        if p.exists():
            with st.expander(f"Metadata Agent 1: docs/{name}"):
                st.json(json.loads(p.read_text(encoding="utf-8")))
    prev = [REPO / "outputs/maps" / n for n in ("lst_2024_preview.png", "ndvi_2024_preview.png", "dynamic_world_preview.png")]
    prev = [p for p in prev if p.exists()]
    if prev:
        st.markdown("**Pratinjau visual Agent 1** (gambar statis dari GEE; bukan hasil agregasi grid dan bukan masukan model):")
        cols = st.columns(len(prev))
        for c, p in zip(cols, prev):
            c.image(str(p), caption=p.name, width="stretch")
    st.markdown(
        "**Kontrak yang ditunggu** — `data/processed/remote_sensing_grid.csv`, satu baris per `grid_id`:\n\n"
        "| kolom | wajib | satuan / makna |\n|---|---|---|\n"
        "| `grid_id` | ya | sama dengan master grid |\n"
        "| `lst_c` | ya | LST °C, statistik per grid (median/mean piksel; dokumentasikan) |\n"
        "| `ndvi` | ya | NDVI −1…1 |\n"
        "| `lst_valid_frac` | opsional | porsi piksel dengan LST valid (0–1); < 0,5 dikeluarkan |\n"
        "| `lst_unc_k`, `lst_obs` | opsional | ketidakpastian ST_QA (K), jumlah observasi valid |\n"
        "| `trees_prob`, `built_prob` | opsional | probabilitas Dynamic World 0–1 (bukan fraksi tutupan) |\n"
    )
    st.stop()

st.subheader("Peta")
opts = {"LST (°C)": ("lst_c", "Oranges", 2), "NDVI": ("ndvi", "Greens", 3)}
for c, lab, cm in (("trees_prob", "Probabilitas pohon (Dynamic World)", "Greens"),
                   ("built_prob", "Probabilitas bangunan (Dynamic World)", "Greys"),
                   ("lst_unc_k", "Ketidakpastian ST_QA (K)", "Purples"),
                   ("lst_obs", "Jumlah observasi LST valid", "Blues"),
                   ("lst_valid_frac", "Porsi piksel LST valid", "Blues")):
    if c in f.columns and f[c].notna().any():
        opts[lab] = (c, cm, 3)
lab = st.selectbox("Variabel", list(opts))
col, cmap, dg = opts[lab]
v = f[col]
maps.choropleth(ctx, f, col, lab, cmap, v.quantile(0.02), v.quantile(0.98), extra=("kota", "lst_c", "ndvi"), digits=dg)
c1, c2 = st.columns(2)
with c1:
    ui.histogram(v, lab, color="#eb6834" if col == "lst_c" else "#1baf7a")
with c2:
    st.dataframe(v.describe().to_frame(lab).round(3), width="stretch")

st.subheader("Ringkasan per kota")
g = f.groupby("kota")
summ = pd.DataFrame({"LST median (°C)": g["lst_c"].median(), "LST p90 (°C)": g["lst_c"].quantile(0.9),
                     "NDVI median": g["ndvi"].median(), "grid tanpa LST": g["lst_c"].apply(lambda s: int(s.isna().sum()))})
if "trees_prob" in f.columns:
    summ["pohon median"] = g["trees_prob"].median()
st.dataframe(summ.round(3).reset_index(), hide_index=True, width="stretch")

st.subheader("Cakupan dan kualitas")
miss = f.loc[~f["valid_rs"], ["grid_id", "kota", "coverage_ratio", "lst_c", "ndvi", "f_lst_low_valid"]]
st.write(f"{len(miss):,} grid tanpa LST/NDVI yang dapat dipakai (dikeluarkan dari semua model; tidak diisi nilai).")
st.dataframe(miss, hide_index=True, width="stretch", height=220)
st.caption(f"Rentang wajar: LST {C.LST_RANGE_C} °C, NDVI {C.NDVI_RANGE}; di luar rentang dikosongkan dan ditandai.")
