"""Peta choropleth grid 500 m dengan pydeck. Data spasial EPSG:32748 diproyeksikan ke EPSG:4326 di context."""
from __future__ import annotations

import math

import matplotlib
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

MISSING_RGBA = [0, 0, 0, 0]  # tanpa isian: basemap terlihat, tidak tertukar dengan kategori abu-abu


def _rgba(hex_or_tuple, alpha=200):
    if isinstance(hex_or_tuple, str):
        h = hex_or_tuple.lstrip("#")
        return [int(h[i:i + 2], 16) for i in (0, 2, 4)] + [alpha]
    r, g, b = hex_or_tuple[:3]
    return [int(255 * r), int(255 * g), int(255 * b), alpha]


def _fmt(v, digits=2):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "kosong"
    if isinstance(v, (bool, np.bool_)):
        return "ya" if v else "tidak"
    if isinstance(v, (int, np.integer)):
        return f"{int(v):,}"
    if isinstance(v, (float, np.floating)):
        return f"{v:,.{digits}f}"
    return str(v)


def gradient_legend(cmap: str, vmin: float, vmax: float, label: str, missing_label: str | None = None, digits: int = 2):
    cm = matplotlib.colormaps[cmap]
    stops = ", ".join(matplotlib.colors.to_hex(cm(t)) for t in np.linspace(0, 1, 7))
    miss = (f"<span style='display:inline-block;width:14px;height:14px;background:#fff;border:1px dashed #888;box-sizing:border-box;"
            f"vertical-align:middle;margin:0 4px 0 16px'></span>{missing_label}") if missing_label else ""
    st.markdown(
        f"<div style='font-size:0.85rem'><b>{label}</b><br>"
        f"<span style='margin-right:6px'>{_fmt(vmin, digits)}</span>"
        f"<span style='display:inline-block;width:180px;height:12px;vertical-align:middle;"
        f"background:linear-gradient(to right, {stops})'></span>"
        f"<span style='margin-left:6px'>{_fmt(vmax, digits)}</span>{miss}</div>",
        unsafe_allow_html=True,
    )


def category_legend(colors: dict, labels: dict | None = None, counts: dict | None = None):
    parts = []
    for k, c in colors.items():
        lab = (labels or {}).get(k, k)
        n = f" ({counts.get(k, 0):,})" if counts is not None else ""
        parts.append(f"<span style='display:inline-block;width:14px;height:14px;background:{c};"
                     f"vertical-align:middle;margin:0 4px 0 10px'></span>{lab}{n}")
    st.markdown("<div style='font-size:0.85rem'>" + "".join(parts) + "</div>", unsafe_allow_html=True)


def _deck(ctx, props: list[dict], colors: list, center=None, height=520):
    ids, feats, c0 = ctx.geometry()
    labels = list(props[0].keys()) if props else []
    key = {lab: f"k{i}" for i, lab in enumerate(labels)}  # kunci aman untuk template tooltip
    features = []
    for f, p, col in zip(feats, props, colors):
        features.append({**f, "properties": {**{key[k]: v for k, v in p.items()}, "fill": col}})
    layer = pdk.Layer(
        "GeoJsonLayer",
        {"type": "FeatureCollection", "features": features},
        pickable=True, stroked=False, filled=True, get_fill_color="properties.fill", auto_highlight=True,
    )
    lat, lon = center or c0
    view = pdk.ViewState(latitude=lat, longitude=lon, zoom=10, pitch=0)
    tip = {"html": "<br>".join(f"<b>{lab}</b>: {{{key[lab]}}}" for lab in labels),
           "style": {"fontSize": "12px"}}
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view, tooltip=tip, map_style=None),
                    height=height)


def choropleth(ctx, df: pd.DataFrame, col: str, label: str, cmap: str = "Oranges", vmin=None, vmax=None,
               extra: tuple = (), missing_label: str = "kosong / tidak dipakai", digits: int = 2, height=520):
    """df: kolom grid_id + col (+ extra untuk tooltip). Grid master tanpa baris -> abu-abu."""
    ids, _, _ = ctx.geometry()
    d = df.set_index("grid_id").reindex(ids)
    v = pd.to_numeric(d[col], errors="coerce")
    lo = float(np.nanmin(v)) if vmin is None and v.notna().any() else (vmin or 0.0)
    hi = float(np.nanmax(v)) if vmax is None and v.notna().any() else (vmax if vmax is not None else 1.0)
    cm = matplotlib.colormaps[cmap]
    span = hi - lo if hi > lo else 1.0
    colors = [MISSING_RGBA if not np.isfinite(x) else _rgba(cm(min(max((x - lo) / span, 0), 1)))
              for x in v.to_numpy(float)]
    props = []
    for gid, row in zip(ids, d.itertuples(index=False)):
        r = row._asdict()
        p = {"grid_id": gid, label: _fmt(r.get(col), digits)}
        for e in extra:
            p[e] = _fmt(r.get(e), digits)
        props.append(p)
    _deck(ctx, props, colors, height=height)
    gradient_legend(cmap, lo, hi, label, missing_label, digits)


def categorical(ctx, df: pd.DataFrame, col: str, colors: dict, label: str, labels: dict | None = None,
                extra: tuple = (), missing_label: str = "kosong / tidak dipakai", height=520):
    ids, _, _ = ctx.geometry()
    d = df.set_index("grid_id").reindex(ids)
    cats = d[col]
    cols = [_rgba(colors[c]) if (isinstance(c, str) and c in colors) else MISSING_RGBA for c in cats]
    props = []
    for gid, row in zip(ids, d.itertuples(index=False)):
        r = row._asdict()
        c = r.get(col)
        p = {"grid_id": gid, label: (labels or {}).get(c, c) if isinstance(c, str) else missing_label}
        for e in extra:
            p[e] = _fmt(r.get(e))
        props.append(p)
    _deck(ctx, props, cols, height=height)
    counts = cats.value_counts().to_dict()
    category_legend({**colors, "__na": "#fff;border:1px dashed #888;box-sizing:border-box"}, {**(labels or {}), "__na": missing_label},
                    {**counts, "__na": int(cats.isna().sum() + (~cats.isin(list(colors)) & cats.notna()).sum())})
