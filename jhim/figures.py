"""Figur matplotlib tanpa data spasial (dipakai dashboard dan ekspor paper)."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402


def matrix_heatmap(mat: pd.DataFrame, title: str, vmin=0.0, vmax=1.0, cmap="viridis"):
    fig, ax = plt.subplots(figsize=(4.6, 4.0), dpi=120)
    im = ax.imshow(mat.to_numpy(float), vmin=vmin, vmax=vmax, cmap=cmap)
    ax.set_xticks(range(len(mat.columns)), mat.columns)
    ax.set_yticks(range(len(mat.index)), mat.index)
    mid = (vmin + vmax) / 2
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat.iat[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=9,
                    color="white" if v < mid else "black")
    ax.set_title(title, fontsize=11)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    return fig


def rank_scatter(shift: pd.DataFrame, a: str, b: str, top_n: int | None = None):
    """Peringkat model a (x) vs model b (y). Grid di bawah diagonal naik prioritas di model b."""
    fig, ax = plt.subplots(figsize=(5.2, 5.0), dpi=120)
    colors = {"tetap top": "#b2182b", f"masuk top di {b.upper()}": "#ef8a62",
              f"keluar top di {b.upper()}": "#67a9cf", "bukan top": "#bdbdbd"}
    for t, c in colors.items():
        s = shift[shift["transisi"] == t]
        ax.scatter(s["rank_a"], s["rank_b"], s=6, c=c, label=f"{t} ({len(s)})", linewidths=0)
    n = int(max(shift["rank_a"].max(), shift["rank_b"].max()))
    ax.plot([1, n], [1, n], color="black", lw=0.7, ls="--")
    if top_n:
        ax.axvline(top_n, color="grey", lw=0.6)
        ax.axhline(top_n, color="grey", lw=0.6)
    ax.set_xlabel(f"Peringkat {a.upper()} (1 = prioritas tertinggi)")
    ax.set_ylabel(f"Peringkat {b.upper()}")
    ax.set_title(f"Perubahan peringkat {a.upper()} ke {b.upper()}", fontsize=11)
    ax.legend(fontsize=7, markerscale=2, loc="lower right")
    fig.tight_layout()
    return fig


def coverage_bars(cov: pd.DataFrame):
    c = cov[cov["kelompok"].str.endswith(" top")]
    x = np.arange(len(c))
    fig, ax = plt.subplots(figsize=(5.4, 3.6), dpi=120)
    ax.bar(x - 0.2, c["pct_populasi_valid"], 0.4, label="% penduduk", color="#4575b4")
    ax.bar(x + 0.2, c["pct_rentan_valid"], 0.4, label="% penduduk rentan (0-14, 65+)", color="#d73027")
    ax.set_xticks(x, [k.replace(" top", "") for k in c["kelompok"]])
    ax.set_ylabel("% dari seluruh grid valid")
    ax.set_title("Penduduk yang berada di grid prioritas teratas", fontsize=11)
    ax.legend(fontsize=8)
    fig.tight_layout()
    return fig


def sensitivity_bars(summ: pd.DataFrame, stable_ref: float | None = None):
    s = summ.sort_values("jaccard_vs_baseline")
    fig, ax = plt.subplots(figsize=(6.0, 0.32 * len(s) + 1.2), dpi=120)
    ax.barh(s["skenario"], s["jaccard_vs_baseline"], color="#4575b4")
    ax.set_xlim(0, 1)
    ax.set_xlabel("Jaccard 10% teratas vs baseline")
    ax.set_title("Stabilitas prioritas terhadap skenario", fontsize=11)
    if stable_ref:
        ax.axvline(stable_ref, color="grey", ls="--", lw=0.8)
    fig.tight_layout()
    return fig
