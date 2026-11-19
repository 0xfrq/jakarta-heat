"""Elemen UI bersama: banner mode/status, pemberitahuan masukan tertunda, unduhan tabel."""
from __future__ import annotations

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from .context import Ctx

STATE_ICON = {"INVALID": ":material/error:", "P2_ONLY": ":material/hourglass_top:",
              "RS_INCOMPLETE": ":material/warning:", "COMPLETE": ":material/check_circle:"}


def banner(ctx: Ctx):
    st.caption("Eksploratif, lima kota daratan: LST/NDVI dan demografi 2024; proksi jaringan/taman kandidat OSM "
               "19 November 2026. Bukan akses publik 2024 terverifikasi, paparan individu, atau risiko kesehatan.")
    if ctx.demo:
        st.error("**MODE DEMO — DATA SINTETIS.** Semua angka, peta, dan skor di mode ini berasal dari data dummy "
                 "(`is_dummy=1`) untuk menguji perangkat lunak. **Bukan hasil penelitian** dan tidak boleh dikutip.",
                 icon=":material/science:")
    s = ctx.status
    msg = f"**Status masukan: {s.state}** — {s.text}"
    if s.state == "INVALID":
        st.error(msg + "\n\n" + "\n".join(f"- {e}" for e in s.errors), icon=STATE_ICON[s.state])
    elif s.state == "P2_ONLY":
        st.info(msg, icon=STATE_ICON[s.state])
    elif s.state == "RS_INCOMPLETE":
        st.warning(msg, icon=STATE_ICON[s.state])
    elif s.state == "COMPLETE":
        st.success(msg, icon=STATE_ICON[s.state])
    qa = [n for n in s.notes if "DIKELUARKAN aturan QA" in n]
    for n in qa:
        st.caption(n)
    if ctx.feat is not None:
        f = ctx.feat
        if "qa_age_source_no_support" in f:
            st.warning(f"Dukungan sumber usia tidak tersedia pada {int(f['qa_age_source_no_support'].sum())} grid. "
                       "Nilai analitis null; nol ekspor mentah bukan bukti tidak ada penduduk. "
                       f"Perbandingan M1-M4 memakai {int(f['valid'].sum()):,} grid bersama.")
        else:
            st.warning("Dukungan raster demografi belum terintegrasi. Nilai nol lama belum membuktikan populasi nol; "
                       "skor yang tersedia masih provisional dan memerlukan koreksi dukungan sumber.")
    st.caption("Bobot dan kebijakan ilmiah belum disahkan tim. Frekuensi skenario bukan probabilitas keyakinan; "
               "sensitivitas akses tujuan/pintu masuk harus dinilai terpisah.")


def pending(what: str):
    st.warning(
        f"**{what} belum tersedia untuk data asli.** Membutuhkan `data/processed/remote_sensing_grid.csv` dari Agent 1 "
        "(kolom wajib `grid_id, lst_c, ndvi`). Tidak ada nilai pengganti yang ditampilkan. "
        "Untuk melihat fungsi halaman ini, pilih mode **DEMO (data sintetis)** di sidebar.",
        icon=":material/hourglass_top:",
    )


def download(df: pd.DataFrame, name: str, ctx: Ctx, label: str = "Unduh CSV"):
    prefix = "DEMO_" if ctx.demo else ""
    out = df.copy()
    out["reference_scope"] = "DEMO synthetic" if ctx.demo else "thermal_demography_2024_OSM_2026-11-19_candidate_proxy"
    out["scientific_policy"] = "provisional_unsigned"
    st.download_button(label, out.to_csv(index=False).encode("utf-8"), f"{prefix}{name}.csv", "text/csv",
                       key=f"dl_{name}")


def histogram(series: pd.Series, title: str, bins: int = 30, color: str = "#2a78d6", height: int = 220):
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        st.caption(f"{title}: tidak ada nilai.")
        return
    cnt, edges = np.histogram(s, bins=bins)
    d = pd.DataFrame({"mulai": edges[:-1], "akhir": edges[1:], "n": cnt})
    ch = (alt.Chart(d).mark_rect(color=color, stroke="white", strokeWidth=1)
          .encode(x=alt.X("mulai:Q", title=title, scale=alt.Scale(zero=False)), x2="akhir:Q",
                  y=alt.Y("n:Q", title="jumlah grid"), y2=alt.datum(0),
                  tooltip=[alt.Tooltip("mulai:Q", title="dari", format=",.2f"),
                           alt.Tooltip("akhir:Q", title="sampai", format=",.2f"), alt.Tooltip("n:Q", title="jumlah grid")])
          .properties(height=height))
    st.altair_chart(ch, width="stretch")


def matrix(df: pd.DataFrame, fmt: str = "{:.3f}"):
    st.dataframe(df.style.format(fmt).background_gradient(cmap="Blues", vmin=0, vmax=1), width="stretch")
