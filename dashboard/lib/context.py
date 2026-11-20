"""Pemuatan data ter-cache untuk dashboard. Semua logika ilmiah ada di paket `jhim`; modul ini hanya
memanggilnya dan menyimpan hasil di cache Streamlit (kunci cache memuat waktu ubah berkas masukan).
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import streamlit as st

from . import REPO  # noqa: F401  (menambahkan akar repo ke sys.path)
from jhim import compare as K  # noqa: E402
from jhim import config as C  # noqa: E402
from jhim import data as D  # noqa: E402
from jhim import models as M  # noqa: E402

MODE_REAL, MODE_DEMO = "Data asli", "DEMO (data sintetis)"


def _sig(paths: C.Paths) -> tuple:
    from jhim.provenance import inputs_identity, implementation_identity, digest, scientific_config

    return (digest(inputs_identity(paths)), implementation_identity()["sha256"], digest(scientific_config()))


@st.cache_data(show_spinner="Memuat dan memvalidasi data ...")
def _features(demo: bool, unreachable: str, sig: tuple):
    paths = C.Paths(demo=demo)
    status = D.assess_inputs(paths)
    if status.state == D.INVALID:
        return None, None, status
    feat, meta, status = D.load_features(paths, unreachable)
    return feat, meta, status


@st.cache_data(show_spinner="Memuat geometri grid ...")
def _geometry(demo: bool, sig: tuple):
    """Fitur GeoJSON EPSG:4326 (pydeck butuh lon/lat) tanpa properti; properti ditempel per peta."""
    paths = C.Paths(demo=demo)
    g = D.read_grid_gdf(paths.grid).to_crs(C.CRS_WEB)
    gj = g.__geo_interface__
    ids = g[C.KEY].tolist()
    feats = [{"type": "Feature", "geometry": f["geometry"]} for f in gj["features"]]
    b = g.total_bounds
    return ids, feats, (float((b[1] + b[3]) / 2), float((b[0] + b[2]) / 2))


@st.cache_data(show_spinner="Menghitung skor M1-M4 ...")
def _priority(demo: bool, unreachable: str, sig: tuple):
    feat, _, status = _features(demo, unreachable, sig)
    if feat is None or not status.can_model or not feat["valid"].any():
        return None
    return M.build_priority_table(feat)


@st.cache_data(show_spinner="Menjalankan uji sensitivitas (sekali per model) ...")
def sensitivity(demo: bool, unreachable: str, sig: tuple, model: str):
    from jhim import sensitivity as SE

    feat, _, _ = _features(demo, unreachable, sig)
    return SE.run_sensitivity(feat, model)


@st.cache_data(show_spinner="Menghitung Moran's I ...")
def moran(demo: bool, sig: tuple, values: pd.DataFrame, cols: tuple, kinds: tuple, perms: int):
    from jhim import spatial as SP

    paths = C.Paths(demo=demo)
    g = D.read_grid_gdf(paths.grid).merge(values, on=C.KEY, how="inner", validate="one_to_one")
    return SP.moran_table(g, list(cols), kinds, perms)


@st.cache_data(show_spinner="Menghitung LISA ...")
def lisa(demo: bool, sig: tuple, values: pd.DataFrame, col: str, kind: str, perms: int, alternative="directed"):
    from jhim import spatial as SP

    paths = C.Paths(demo=demo)
    g = D.read_grid_gdf(paths.grid).merge(values, on=C.KEY, how="inner", validate="one_to_one")
    return SP.lisa_for(g, col, kind, perms, alternative=alternative)


@dataclass
class Ctx:
    demo: bool
    unreachable: str
    paths: C.Paths
    sig: tuple
    feat: pd.DataFrame | None
    meta: dict | None
    status: D.InputStatus

    @property
    def can_model(self) -> bool:
        return self.feat is not None and self.status.can_model and bool(self.feat["valid"].any())

    def priority(self) -> pd.DataFrame | None:
        return _priority(self.demo, self.unreachable, self.sig) if self.can_model else None

    def geometry(self):
        return _geometry(self.demo, self.sig)

    def pri_feat(self) -> pd.DataFrame | None:
        pri = self.priority()
        if pri is None:
            return None
        return pri.merge(self.feat.drop(columns=["valid"]), on=C.KEY, how="left", validate="one_to_one")


def get_ctx() -> Ctx:
    """Konteks halaman. Mode dan kebijakan diambil dari session_state (diatur di sidebar app.py)."""
    mode = st.session_state.get("mode", MODE_REAL)
    unreachable = st.session_state.get("unreachable", "exclude")
    demo = mode == MODE_DEMO
    paths = C.Paths(demo=demo)
    sig = _sig(paths)
    feat, meta, status = _features(demo, unreachable, sig)
    return Ctx(demo, unreachable, paths, sig, feat, meta, status)


def model_keys(pri) -> list[str]:
    return K.model_keys(pri)
