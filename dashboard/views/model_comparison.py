import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st  # noqa: E402

from jhim import figures as F  # noqa: E402
from lib import maps, ui  # noqa: E402
from lib.context import C, K, get_ctx  # noqa: E402

ctx = get_ctx()
st.title("Perbandingan model")
ui.banner(ctx)
if not ctx.can_model:
    ui.pending("Perbandingan M1–M4")
    st.stop()

pri = ctx.priority()
feat = ctx.feat
nv = int(pri["valid"].sum())
st.write(f"Semua metrik dihitung pada **himpunan grid valid bersama** ({nv:,} grid), sehingga tidak ada "
         "korelasi antar-model yang dihitung pada subset grid berbeda.")
top_frac = st.select_slider("Ambang prioritas tinggi", [0.05, 0.10, 0.20], value=0.10, format_func=lambda x: f"top {x:.0%}")
p = K.retop(pri, top_frac)

st.subheader("Korelasi peringkat")
c1, c2 = st.columns(2)
with c1:
    st.markdown("**Spearman ρ (skor)**")
    ui.matrix(K.spearman_matrix(p))
with c2:
    st.markdown("**Kendall τ-b (skor)**")
    ui.matrix(K.kendall_matrix(p))

st.subheader("Overlap himpunan prioritas tinggi")
c1, c2 = st.columns(2)
with c1:
    st.markdown(f"**Jaccard top {top_frac:.0%}**")
    ui.matrix(K.jaccard_matrix(p))
with c2:
    st.markdown("**Overlap pada beberapa ambang**")
    ov = K.overlap_table(pri)
    st.dataframe(ov.round(3), hide_index=True, width="stretch", height=260)
    ui.download(ov, "top_overlap", ctx)

st.subheader("Perpindahan peringkat")
st.dataframe(K.rank_movement(pri).round(1), hide_index=True, width="stretch")

c1, c2 = st.columns(2)
a = c1.selectbox("Model awal", ["M1", "M2", "M3"], index=0).lower()
b = c2.selectbox("Model pembanding", ["M2", "M3", "M4"], index=2).lower()
if a == b:
    st.stop()
sh = K.rank_shift(p, a, b)
lim = max(float(sh["shift"].abs().quantile(0.98)), 1.0)
st.markdown(f"**Peta perubahan peringkat {a.upper()} → {b.upper()}** (merah = naik prioritas di {b.upper()})")
maps.choropleth(ctx, sh, "shift", f"peringkat {a.upper()} − peringkat {b.upper()}", "RdBu_r", -lim, lim,
                extra=("rank_a", "rank_b", "transisi"), missing_label="tidak masuk himpunan pembanding", digits=0)

st.markdown(f"**Transisi top {top_frac:.0%}**")
tcol = {"tetap top": "#b2182b", f"masuk top di {b.upper()}": "#eb6834", f"keluar top di {b.upper()}": "#2a78d6"}
maps.categorical(ctx, sh.loc[sh["transisi"] != "bukan top"], "transisi", tcol, "transisi",
                 extra=("rank_a", "rank_b"), missing_label="bukan top di kedua model / tidak dipakai")

c1, c2 = st.columns(2)
with c1:
    st.markdown("**Matriks transisi kelas (jumlah grid)**")
    tm = K.transition_matrix(pri, a, b)
    st.dataframe(tm, width="stretch")
with c2:
    st.pyplot(F.rank_scatter(sh, a, b, int(p[f"{a}_top"].sum())), width="stretch")

st.subheader("Profil grid: hanya panas vs sadar-kerentanan")
hv = K.heat_vs_aware(p, feat, a, b)
st.dataframe(hv.round(2), hide_index=True, width="stretch")
st.caption("Deskriptif. Perbedaan profil menunjukkan apa yang diubah oleh model, bukan siapa yang paling terdampak secara kesehatan.")

st.subheader("Sebaran per kota")
ks = K.kota_summary(p, feat)
st.pyplot(F.kota_bars(ks), width="stretch")
st.dataframe(ks.round(1), hide_index=True, width="stretch", height=260)
ui.download(ks, "kota_summary", ctx)
