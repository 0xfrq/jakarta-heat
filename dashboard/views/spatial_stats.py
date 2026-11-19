import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from jhim import figures as F  # noqa: E402
from jhim import spatial as SP  # noqa: E402
from lib import context, maps, ui  # noqa: E402
from lib.context import C, get_ctx  # noqa: E402

ctx = get_ctx()
st.title("Statistik spasial")
ui.banner(ctx)
f = ctx.feat
if f is None:
    st.stop()

st.markdown(
    "**Bobot baseline: Queen contiguity** pada poligon grid (sel berbagi sisi atau titik sudut), distandardisasi "
    "baris. Grid reguler 500 m membuat Queen (≤ 8 tetangga) simetris dan mudah dijelaskan; Rook (≤ 4) dan "
    "KNN-8 dipakai sebagai sensitivitas. Grid tanpa tetangga (*islands*) dikeluarkan dan dilaporkan. "
    "p-value berbasis permutasi bersyarat dengan seed tetap."
)

vals = pd.DataFrame({C.KEY: f[C.KEY]})
labels = {}
pri = ctx.priority()
if pri is not None:
    for k in ("m1", "m2", "m3", "m4"):
        vals[f"{k}_score"] = pri.set_index(C.KEY)[f"{k}_score"].reindex(f[C.KEY]).to_numpy()
        labels[f"{k}_score"] = f"Skor {k.upper()}"
    for c, lab in (("lst_c", "LST (°C)"), ("ndvi", "NDVI")):
        vals[c] = f[c].to_numpy()
        labels[c] = lab
vals["log1p_population"] = np.log1p(f["population"]).to_numpy()
vals["log1p_pop_vulnerable"] = np.log1p(f["pop_vulnerable"]).to_numpy()
vals["vuln_share"] = f["vuln_share"].to_numpy()
vals["park_distance_m"] = f["park_distance_m"].to_numpy()
labels.update({"log1p_population": "log1p penduduk", "log1p_pop_vulnerable": "log1p penduduk rentan",
               "vuln_share": "porsi penduduk rentan", "park_distance_m": "jarak taman (m; tanpa grid rute kosong)"})
if pri is None:
    st.info("Skor model belum tersedia untuk data asli; halaman ini menampilkan variabel Person 2 saja "
            "(deskriptif). Skor M1–M4 muncul setelah data remote sensing tersedia.")

c1, c2 = st.columns([2, 1])
sel = c1.multiselect("Variabel", list(labels), default=list(labels)[:4], format_func=labels.get)
kinds = c2.multiselect("Definisi tetangga", list(C.SPATIAL_WEIGHTS), default=list(C.SPATIAL_WEIGHTS))
perms = c2.select_slider("Permutasi", [99, 499, 999, 9999], value=999)
if sel and kinds:
    gm = context.moran(ctx.demo, ctx.sig, vals[[C.KEY, *sel]], tuple(sel), tuple(kinds), perms)
    gm["variabel"] = gm["variabel"].map(labels)
    st.subheader("Moran's I global")
    st.dataframe(gm[["variabel", "bobot", "n", "n_islands_dikeluarkan", "I", "EI", "z_sim", "p_sim", "mean_neighbors"]]
                 .round(4), hide_index=True, width="stretch")
    st.caption(f"p_sim minimum yang mungkin = 1/({perms}+1) = {1 / (perms + 1):.4f}. "
               "I > E[I] menunjukkan nilai serupa cenderung berdekatan.")
    ui.download(gm, "moran_global", ctx)

st.subheader("LISA (Local Moran's I)")
c1, c2, c3 = st.columns(3)
var = c1.selectbox("Variabel LISA", list(labels), format_func=labels.get)
kind = c2.selectbox("Tetangga", list(C.SPATIAL_WEIGHTS), index=0)
sig = c3.radio("Signifikansi", ["FDR Benjamini–Hochberg (q = 0,05)", "BY konservatif (q = 0,05)", "p < 0,05 tanpa koreksi"])
alternative = st.selectbox("Alternatif LISA (provisional)", ["directed", "two-sided"])
st.caption("Global: hipotesis autokorelasi positif (ekor atas). LISA: alternatif eksplisit, koreksi per peta pada "
           "semua grid layak tanpa island. BH memerlukan asumsi dependensi; BY adalah sensitivitas konservatif.")
lisa, dropped = context.lisa(ctx.demo, ctx.sig, vals[[C.KEY, var]], var, kind, perms, alternative)
colc = "klaster_fdr" if sig.startswith("FDR") else "klaster_by" if sig.startswith("BY") else "klaster_p05"
show = lisa.copy()
# Tested-but-not-significant ("ns") is a test result; grids outside the tested set stay a separate unknown state.
show["klaster"] = show[colc]
maps.categorical(ctx, show, "klaster", dict(F.LISA_COLORS), "klaster LISA",
                 labels={**SP.LISA_LABELS, "ns": "tidak signifikan (diuji)"}, extra=("lisa_I", "p_sim"),
                 missing_label="tidak diuji (tidak layak / island)")
n_sig = int((lisa[colc] != "ns").sum())
sig_short = "BH" if colc == "klaster_fdr" else "BY" if colc == "klaster_by" else "p<0,05"
st.caption(f"{n_sig:,} dari {len(lisa):,} grid yang diuji signifikan ({sig_short}, alternatif {alternative}, "
           f"{perms} permutasi); {len(f) - len(lisa):,} grid tidak diuji.")
if n_sig == 0 and colc != "klaster_p05":
    st.info(f"Tidak ada klaster lolos koreksi {sig_short}. Dengan {perms} permutasi, p terkecil yang mungkin adalah "
            f"1/({perms}+1) = {1 / (perms + 1):.4f}; koreksi konservatif dapat bernilai nol karena resolusi permutasi, "
            "bukan bukti tidak ada pola. Bandingkan dengan 9999 permutasi (tabel sensitivitas kandidat).")
cnt = pd.crosstab(lisa["klaster_p05"], lisa[colc], rownames=["p<0,05"], colnames=[sig_short])
st.dataframe(cnt, width="stretch")
if dropped:
    st.caption(f"Islands dikeluarkan ({len(dropped)}): {', '.join(dropped[:10])}")
st.markdown(
    "**Interpretasi.** LISA diuji pada setiap grid (ribuan uji), sehingga label tanpa koreksi akan memuat banyak "
    "positif palsu; klaim memakai kolom FDR. Klaster adalah pola deskriptif nilai yang mirip/berbeda dengan "
    "tetangganya — **bukan** penjelasan kausal. Hasil bergantung pada definisi tetangga dan unit grid 500 m "
    "(masalah unit areal yang dapat dimodifikasi/MAUP)."
)
ui.download(lisa, f"lisa_{var}_{kind}", ctx)
