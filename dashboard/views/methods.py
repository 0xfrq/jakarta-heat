import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st  # noqa: E402

from lib import REPO, ui  # noqa: E402
from lib.context import C, get_ctx  # noqa: E402

ctx = get_ctx()
st.title("Metode dan keterbatasan")
ui.banner(ctx)
doc = REPO / "docs/agent3_methods.md"
if doc.exists():
    st.markdown(doc.read_text(encoding="utf-8"))
else:
    st.error(f"Dokumen metode tidak ditemukan: {doc}")
with st.expander("Konfigurasi aktif (jhim/config.py)"):
    st.json(C.config_snapshot())
if ctx.meta:
    with st.expander("Metadata pemuatan data saat ini"):
        st.json(ctx.meta)
