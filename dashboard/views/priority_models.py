import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from lib import maps, ui  # noqa: E402
from lib.context import C, M, get_ctx  # noqa: E402

ctx = get_ctx()
st.title("Model prioritas M1–M4")
ui.banner(ctx)

st.dataframe(pd.DataFrame([{"model": m, "rumus": C.MODEL_FORMULAS[m],
                            "bobot": ", ".join(f"{k}={v:.2f}" for k, v in C.MODELS[m].items())} for m in C.MODELS]),
             hide_index=True, width="stretch")
st.caption(C.WEIGHTS_STATUS)
with st.expander("Definisi komponen dan arah"):
    st.markdown(
        "- `n(x)` = min-max setelah dipotong persentil 5 dan 95 **pada himpunan grid valid bersama**; 0–1.\n"
        "- LST tinggi → prioritas tinggi. NDVI rendah → prioritas tinggi (`1 − n(NDVI)`).\n"
        "- Populasi dan penduduk rentan memakai `log1p(jumlah)` agar skala jumlah tidak mendominasi.\n"
        "- Defisit taman = `min(jarak, 1000 m) / 1000` (tidak dinormalisasi ulang: 0 m → 0, ≥ 1 km → 1).\n"
        "- Peringkat 1 = prioritas tertinggi; seri dipecah oleh skor tanpa pemotongan, lalu `grid_id`.\n"
        "- Kelas: top 10% / 10–25% / 25–50% / 50–100% dari grid valid (PROVISIONAL)."
    )

if not ctx.can_model:
    ui.pending("Skor M1–M4")
    st.stop()

f = ctx.feat
v = f.loc[f["valid"]]
st.write(f"Himpunan pembanding bersama: **{len(v):,}** dari {len(f):,} grid "
         f"(kebijakan jarak taman kosong: `{ctx.unreachable}`).")

c1, c2, c3 = st.columns([1, 1, 1])
model = c1.selectbox("Model", list(C.MODELS), index=3, format_func=C.MODEL_LABELS.get)
top_frac = c2.select_slider("Bagian prioritas tinggi", options=[0.05, 0.10, 0.15, 0.20, 0.25], value=0.10,
                            format_func=lambda x: f"top {x:.0%}")
view = c3.radio("Tampilan peta", ["Skor 0–1", "Kelas prioritas", "Top-N"])

custom = st.toggle("Bobot eksploratif (bukan baseline)", value=False)
weights = dict(C.MODELS[model])
if custom:
    st.warning("**EKSPLORATIF** — bobot di bawah diubah pengguna; hasil bukan baseline dan tidak untuk dikutip.")
    cols = st.columns(len(weights))
    for c, k in zip(cols, list(weights)):
        weights[k] = c.slider(C.COMPONENT_LABELS.get(k, k), 0.0, 1.0, float(weights[k]), 0.05, key=f"w_{model}_{k}")
    if sum(weights.values()) <= 0:
        st.error("Jumlah bobot harus > 0.")
        st.stop()
    weights = M.normalize_weights(weights)
    st.caption("Bobot dinormalisasi ulang: " + ", ".join(f"{k}={w:.2f}" for k, w in weights.items()))

score, rank = M.score_rank(v, weights)
res = v[["grid_id", "kota", "lst_c", "ndvi", "population", "pop_vulnerable", "park_distance_m", "f_snap_far",
         "f_low_coverage"]].copy()
res["skor"], res["peringkat"] = score, rank
res["skor_pemecah_seri"] = M.weighted_score(M.components(v, clip=None), weights)
res["kelas"] = M.priority_class(rank, len(v)).to_numpy()
res["top"] = M.top_mask(rank, len(v), top_frac)
nt = int(res["top"].sum())

c1, c2, c3 = st.columns(3)
c1.metric(f"Grid top {top_frac:.0%}", f"{nt:,}")
c2.metric("Penduduk di grid top", f"{res.loc[res['top'], 'population'].sum():,.0f}")
c2.caption(f"{100 * res.loc[res['top'], 'population'].sum() / res['population'].sum():.1f}% dari penduduk grid valid")
c3.metric("Penduduk rentan di grid top", f"{res.loc[res['top'], 'pop_vulnerable'].sum():,.0f}")

extra = ("kota", "peringkat", "lst_c", "ndvi", "population", "park_distance_m")
if view == "Skor 0–1":
    maps.choropleth(ctx, res, "skor", f"skor {model}", "Oranges", 0.0, 1.0, extra=extra,
                    missing_label="tidak masuk himpunan pembanding")
elif view == "Kelas prioritas":
    colors = dict(zip(C.CLASS_LABELS, ["#a63603", "#e6550d", "#fdae6b", "#feedde"]))
    maps.categorical(ctx, res, "kelas", colors, f"kelas {model}", extra=extra,
                     missing_label="tidak masuk himpunan pembanding")
else:
    res["top_lab"] = res["top"].map({True: "top", False: "lainnya"})
    maps.categorical(ctx, res, "top_lab", {"top": "#b2182b", "lainnya": "#d0d0d0"}, f"top {top_frac:.0%} {model}",
                     labels={"top": f"top {top_frac:.0%}", "lainnya": "grid valid lainnya"}, extra=extra,
                     missing_label="tidak masuk himpunan pembanding")

c1, c2 = st.columns(2)
with c1:
    ui.histogram(res["skor"], f"skor {model}", color="#eb6834")
with c2:
    st.markdown("**Grid per kelas**")
    st.dataframe(res["kelas"].value_counts().sort_index().rename("jumlah grid"), width="stretch")

st.subheader(f"Grid prioritas tertinggi ({model})")
top = res.loc[res["top"]].sort_values("peringkat")
st.dataframe(top, hide_index=True, width="stretch", height=320)
st.caption("Kolom f_snap_far / f_low_coverage menandai grid yang perlu QA Person 2 sebelum ditafsirkan. "
           f"{int((res['skor'] >= 1.0).sum())} grid jenuh pada skor 1,0 akibat pemotongan persentil 5–95; "
           "urutannya ditentukan oleh `skor_pemecah_seri` (min-max tanpa pemotongan), lalu grid_id.")
ui.download(top, f"top_{model.lower()}{'_eksploratif' if custom else ''}", ctx)
