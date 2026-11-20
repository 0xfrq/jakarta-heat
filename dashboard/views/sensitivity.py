import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import altair as alt  # noqa: E402
import streamlit as st  # noqa: E402

from lib import context, maps, ui  # noqa: E402
from lib.context import C, get_ctx  # noqa: E402

ctx = get_ctx()
st.title("Robustness / sensitivitas")
ui.banner(ctx)
st.warning("Ringkasan halaman ini hanya skenario one-at-a-time yang tersedia. Median Jaccard atau frekuensi stabil "
           "tidak menyatakan ketahanan terhadap semua definisi akses. Tujuan, pintu masuk, dan hambatan jaringan "
           "menunggu integrasi versi GIS; hasil gabungan ada pada tabel remediasi per keluarga.")
st.markdown(
    "Analisis **eksploratif one-at-a-time**: setiap skenario mengubah satu keputusan metodologis lalu "
    "membandingkan himpunan prioritas tinggi dengan baseline. Tujuannya melaporkan stabilitas **dan** "
    "ketidakstabilan — bukan membuktikan bahwa model tertentu lebih baik."
)
if not ctx.can_model:
    ui.pending("Uji sensitivitas skor")
    st.markdown("Skenario yang akan dijalankan (per model M2–M4, bila komponennya relevan): bobot ×0,8/×1,2 dan "
                "bobot sama rata; normalisasi min-max murni, persentil 1–99, peringkat persentil; akses taman biner "
                "500/1000 m dan batas jenuh 750/1500 m; jarak kosong = defisit maksimum / median; kepadatan vs jumlah "
                "penduduk; porsi rentan vs jumlah; Dynamic World menggantikan NDVI; eksklusi snap > 250 m dan "
                "coverage < 10%; Jaccard pada top 5/10/20%.")
    st.stop()

model = st.selectbox("Model", ["M2", "M3", "M4"], index=2, format_func=C.MODEL_LABELS.get)
summ, stab, info = context.sensitivity(ctx.demo, ctx.unreachable, ctx.sig, model)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Skenario", info["n_scenarios"])
c2.metric("Jaccard top 10% median", f"{info['median_jaccard']:.2f}")
c3.metric("Jaccard terendah", f"{info['min_jaccard']:.2f}")
c4.metric(f"Grid top stabil (≥ {C.STABLE_SHARE:.0%} skenario)", f"{info['share_baseline_top_stable']:.0%}")

frac = st.radio("Ambang", [c for c in summ.columns if c.startswith("jaccard_top")], horizontal=True, index=1)
d = summ.sort_values(frac).assign(label=lambda x: x["kelompok"] + " · " + x["skenario"])
ch = (alt.Chart(d).mark_bar(color="#2a78d6", cornerRadiusTopRight=3, cornerRadiusBottomRight=3, size=14)
      .encode(x=alt.X(f"{frac}:Q", scale=alt.Scale(domain=[0, 1]), title="Jaccard vs baseline (1 = identik)"),
              y=alt.Y("label:N", sort=None, title=None, axis=alt.Axis(labelLimit=420, labelOverlap=False)),
              tooltip=["skenario", "kelompok", alt.Tooltip(f"{frac}:Q", format=".3f"),
                       alt.Tooltip("spearman_vs_baseline:Q", format=".3f"), "n_layak", "n_tambah_vs_baseline",
                       "top_dari_grid_tambahan"])
      .properties(height=20 * len(d) + 40))
st.altair_chart(ch, width="stretch")
st.dataframe(summ.round(3), hide_index=True, width="stretch", height=300)
ui.download(summ, f"sensitivity_{model.lower()}_summary", ctx)

st.subheader("Stabilitas grid prioritas baseline")
s = stab.loc[stab["baseline_top"]]
maps.choropleth(ctx, s, "stable_share", "porsi skenario tetap top", "Blues", 0.0, 1.0,
                extra=("baseline_rank", "n_skenario_layak"), missing_label="bukan top baseline")
st.caption("Skenario 'jarak kosong' menambah grid yang semula dikeluarkan; perlakuan itu adalah asumsi, "
           "bukan pengamatan, sehingga grid tambahan yang masuk top perlu ditinjau secara manual.")
