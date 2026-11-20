"""Figur matplotlib (dipakai dashboard dan ekspor paper).

Konvensi warna:
- Kategorikal (model M1-M4, urutan tetap): biru, oranye, aqua, kuning.
- Sekuensial (besaran): satu hue terang->gelap ("Oranges" untuk skor/LST, "Blues" untuk penduduk,
  "Greens" untuk NDVI).
- Divergen (naik/turun peringkat): "RdBu_r" dengan titik tengah netral.
- Abu-abu muda = grid tidak dipakai / nilai tidak tersedia (bukan nol).
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from . import config as C  # noqa: E402

SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
MODEL_COLORS = dict(zip(["M1", "M2", "M3", "M4"], SERIES))
MISSING = "#ffffff"
# grid yang tidak masuk himpunan pembanding: putih berarsir, agar tidak tertukar dengan kategori abu-abu
MISSING_KW = {"facecolor": "white", "edgecolor": "#a0a0a0", "hatch": "////", "linewidth": 0}
LISA_COLORS = {"HH": "#b2182b", "LL": "#2166ac", "HL": "#f4a582", "LH": "#92c5de", "ns": "#eeeeee"}
TRANSITION_COLORS = {"tetap top": "#b2182b", "masuk": "#eb6834", "keluar": "#2a78d6", "bukan top": "#c8c8c8"}

plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 11,
                     "axes.labelsize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8})


def watermark(fig, text="DATA DUMMY - BUKAN HASIL PENELITIAN"):
    fig.text(0.5, 0.5, text, fontsize=30, color="red", alpha=0.18, ha="center", va="center", rotation=25)


def matrix_heatmap(mat: pd.DataFrame, title: str, vmin=0.0, vmax=1.0, cmap="Blues", fmt="{:.2f}"):
    fig, ax = plt.subplots(figsize=(4.6, 4.0), dpi=120)
    arr = mat.to_numpy(float)
    im = ax.imshow(arr, vmin=vmin, vmax=vmax, cmap=cmap)
    ax.set_xticks(range(len(mat.columns)), mat.columns, rotation=30, ha="right")
    ax.set_yticks(range(len(mat.index)), mat.index)
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            v = arr[i, j]
            if np.isfinite(v):
                frac = (v - vmin) / (vmax - vmin) if vmax > vmin else 0
                ax.text(j, i, fmt.format(v), ha="center", va="center", fontsize=8,
                        color="white" if frac > 0.6 else "black")
    ax.set_title(title)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    return fig


def rank_scatter(shift: pd.DataFrame, a: str, b: str, top_n: int | None = None):
    """Peringkat model a (x) vs model b (y). Grid di bawah diagonal naik prioritas di model b."""
    fig, ax = plt.subplots(figsize=(5.2, 5.0), dpi=120)
    lab = {"tetap top": "tetap top", f"masuk top di {b.upper()}": "masuk", f"keluar top di {b.upper()}": "keluar",
           "bukan top": "bukan top"}
    for t in ["bukan top", f"keluar top di {b.upper()}", f"masuk top di {b.upper()}", "tetap top"]:
        s = shift[shift["transisi"] == t]
        ax.scatter(s["rank_a"], s["rank_b"], s=6, c=TRANSITION_COLORS[lab[t]], label=f"{t} ({len(s)})", linewidths=0)
    n = int(max(shift["rank_a"].max(), shift["rank_b"].max()))
    ax.plot([1, n], [1, n], color="black", lw=0.7, ls="--")
    if top_n:
        ax.axvline(top_n, color="grey", lw=0.6)
        ax.axhline(top_n, color="grey", lw=0.6)
    ax.set_xlabel(f"Peringkat {a.upper()} (1 = prioritas tertinggi)")
    ax.set_ylabel(f"Peringkat {b.upper()}")
    ax.set_title(f"Perubahan peringkat {a.upper()} ke {b.upper()}")
    ax.legend(fontsize=7, markerscale=2, loc="lower right")
    fig.tight_layout()
    return fig


def coverage_bars(cov: pd.DataFrame):
    c = cov[cov["kelompok"].str.endswith(" top")]
    x = np.arange(len(c))
    fig, ax = plt.subplots(figsize=(5.4, 3.6), dpi=120)
    ax.bar(x - 0.21, c["pct_populasi_valid"], 0.4, label="% penduduk", color=SERIES[0])
    ax.bar(x + 0.21, c["pct_rentan_valid"], 0.4, label="% penduduk rentan (0-14, 65+)", color=SERIES[1])
    ax.set_xticks(x, [k.replace(" top", "") for k in c["kelompok"]])
    ax.set_ylabel("% dari seluruh grid valid")
    ax.set_title("Penduduk di grid prioritas teratas")
    ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    return fig


def sensitivity_bars(summ: pd.DataFrame, stable_ref: float | None = None, col: str = "jaccard_vs_baseline"):
    s = summ.sort_values(col)
    fig, ax = plt.subplots(figsize=(6.4, 0.30 * len(s) + 1.3), dpi=120)
    ax.barh(s["skenario"], s[col], color=SERIES[0], height=0.7)
    ax.set_xlim(0, 1)
    ax.set_xlabel("Jaccard himpunan top vs baseline (1 = identik)")
    ax.set_title("Stabilitas prioritas terhadap skenario (eksploratif)")
    if stable_ref:
        ax.axvline(stable_ref, color="grey", ls="--", lw=0.8)
    fig.tight_layout()
    return fig


def score_hist(pri: pd.DataFrame, keys):
    fig, axs = plt.subplots(1, len(keys), figsize=(2.6 * len(keys), 2.6), dpi=120, sharey=True)
    axs = np.atleast_1d(axs)
    v = pri.loc[pri["valid"].astype(bool)]
    for ax, k in zip(axs, keys):
        ax.hist(v[f"{k}_score"].astype(float), bins=30, range=(0, 1), color=MODEL_COLORS[k.upper()])
        ax.set_title(k.upper())
        ax.set_xlabel("skor 0-1")
    axs[0].set_ylabel("jumlah grid")
    fig.suptitle("Distribusi skor prioritas", fontsize=11)
    fig.tight_layout()
    return fig


def kota_bars(ks: pd.DataFrame):
    """% grid prioritas tinggi per kota, per model (batang berdampingan)."""
    kotas = sorted(ks["kota"].dropna().unique())
    models = sorted(ks["model"].unique())
    x = np.arange(len(kotas))
    wdt = 0.8 / max(len(models), 1)
    fig, ax = plt.subplots(figsize=(7.0, 3.6), dpi=120)
    for i, m in enumerate(models):
        d = ks[ks["model"] == m].set_index("kota").reindex(kotas)
        ax.bar(x + (i - (len(models) - 1) / 2) * wdt, d["pct_top_dari_total_top"], wdt * 0.92,
               label=m, color=MODEL_COLORS.get(m, "#888"))
    ax.set_xticks(x, [k.replace("Kota ", "") for k in kotas], rotation=15)
    ax.set_ylabel("% dari seluruh grid top")
    ax.set_title("Sebaran grid prioritas tinggi per kota")
    ax.legend(fontsize=8, frameon=False, ncol=len(models))
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------- peta (butuh geopandas)
def map_grid(geo, values: pd.Series, ids: pd.Series, title: str, cmap="Oranges", vmin=None, vmax=None, ax=None,
             legend=True, label=None):
    g = geo.merge(pd.DataFrame({C.KEY: ids.to_numpy(), "v": values.to_numpy(float)}), on=C.KEY, how="left",
                  validate="one_to_one")
    kw = {"shrink": 0.6}
    if label:
        kw["label"] = label
    g.plot(column="v", cmap=cmap, vmin=vmin, vmax=vmax, ax=ax, linewidth=0, legend=legend,
           legend_kwds=kw, missing_kwds=MISSING_KW)
    ax.set_title(title, fontsize=10)
    ax.set_axis_off()


def map_categories(geo, ids: pd.Series, labels: pd.Series, colors: dict, title: str, ax, legend_labels=None):
    g = geo.merge(pd.DataFrame({C.KEY: ids.to_numpy(), "lab": labels.to_numpy()}), on=C.KEY, how="left",
                  validate="one_to_one")
    g["col"] = g["lab"].map(colors)
    known = g["col"].notna()
    g.loc[known].plot(color=g.loc[known, "col"], ax=ax, linewidth=0)
    if (~known).any():
        g.loc[~known].plot(ax=ax, **MISSING_KW)
    ax.set_title(title, fontsize=10)
    ax.set_axis_off()
    from matplotlib.patches import Patch

    handles = [Patch(facecolor=c, label=(legend_labels or {}).get(k, k)) for k, c in colors.items()]
    handles.append(Patch(label="tidak dipakai / kosong", **MISSING_KW))
    ax.legend(handles=handles, loc="lower left", fontsize=7, frameon=False)
