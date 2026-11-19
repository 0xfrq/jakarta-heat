"""Job 6C: ekspor figur (PNG/SVG) dan tabel untuk bagian Results paper.

    python scripts/07_export_paper.py            # data asli -> outputs/figures, outputs/tables
    python scripts/07_export_paper.py --demo     # latihan (outputs/demo/...)
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from jhim import compare as K  # noqa: E402
from jhim import config as C  # noqa: E402
from jhim import figures as F  # noqa: E402
from jhim import models as M  # noqa: E402
from jhim.data import read_grid_gdf  # noqa: E402
from jhim.io import load_merged, load_priority, run_cli  # noqa: E402
from jhim.util import DataError, write_csv  # noqa: E402

LISA_COLORS = {"HH": "#b2182b", "LL": "#2166ac", "HL": "#f4a582", "LH": "#92c5de", "ns": "#e6e6e6"}


class Saver:
    def __init__(self, folder: Path, formats, dpi, dummy: bool):
        self.folder, self.formats, self.dpi, self.dummy = folder, formats, dpi, dummy
        folder.mkdir(parents=True, exist_ok=True)
        self.written = []

    def __call__(self, fig, name):
        if self.dummy:
            fig.text(0.5, 0.5, "DATA DUMMY", fontsize=48, color="red", alpha=0.18, ha="center", va="center", rotation=25)
        for fmt in self.formats:
            p = self.folder / f"{name}.{fmt}"
            fig.savefig(p, dpi=self.dpi, bbox_inches="tight")
            self.written.append(p)
        plt.close(fig)


def load_geometry(paths: C.Paths):
    return read_grid_gdf(paths.grid).to_crs("EPSG:32748")


def map_grid(geo, values: pd.Series, ids: pd.Series, title: str, cmap="YlOrRd", vmin=None, vmax=None, ax=None, legend=True):
    g = geo.merge(pd.DataFrame({C.KEY: ids.to_numpy(), "v": values.to_numpy(float)}), on=C.KEY, how="left", validate="one_to_one")
    g.plot(column="v", cmap=cmap, vmin=vmin, vmax=vmax, ax=ax, linewidth=0, legend=legend,
           legend_kwds={"shrink": 0.6}, missing_kwds={"color": "#e6e6e6"})
    ax.set_title(title, fontsize=10)
    ax.set_axis_off()


def map_categories(geo, ids: pd.Series, labels: pd.Series, colors: dict, title: str, ax):
    g = geo.merge(pd.DataFrame({C.KEY: ids.to_numpy(), "lab": labels.to_numpy()}), on=C.KEY, how="left", validate="one_to_one")
    g["col"] = g["lab"].map(colors).fillna("#f5f5f5")
    g.plot(color=g["col"], ax=ax, linewidth=0)
    ax.set_title(title, fontsize=10)
    ax.set_axis_off()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--formats", nargs="+", default=["png", "svg"])
    a = ap.parse_args()
    paths = C.Paths(demo=a.demo)
    merged, _ = load_merged(paths)
    pri, meta = load_priority(paths)
    dummy = meta.get("source") == "dummy"
    save = Saver(paths.figures, a.formats, a.dpi, dummy)
    keys = K.model_keys(pri)
    nv, nt = int(pri["valid"].sum()), int(pri["m1_top"].sum())

    # ---- figur tanpa geometri
    save(F.matrix_heatmap(K.spearman_matrix(pri), "Spearman antar skor model", -1.0, 1.0, "RdYlBu_r"), "fig_spearman")
    save(F.matrix_heatmap(K.jaccard_matrix(pri), "Jaccard 10% grid teratas"), "fig_jaccard")
    cov = K.top_coverage(pri, merged)
    save(F.coverage_bars(cov), "fig_coverage_top10")
    save(F.rank_scatter(K.rank_shift(pri, "m1", "m4"), "m1", "m4", nt), "fig_rank_m1_vs_m4")
    sm = paths.tables / "sensitivity_m4_summary.csv"
    if sm.exists():
        save(F.sensitivity_bars(pd.read_csv(sm), C.STABLE_SHARE), "fig_sensitivity_m4")

    # ---- peta
    geo = load_geometry(paths)
    ids = pri[C.KEY]
    fig, axs = plt.subplots(2, 2, figsize=(11, 10))
    for ax, k in zip(axs.ravel(), keys):
        map_grid(geo, pri[f"{k}_score"], ids, C.MODEL_LABELS[k.upper()], "YlOrRd", 0.0, 1.0, ax, legend=True)
    fig.suptitle("Skor prioritas panas (0-1; abu-abu = grid tidak dipakai)", fontsize=12)
    save(fig, "fig_map_scores_m1_m4")

    fig, axs = plt.subplots(2, 2, figsize=(11, 10))
    for ax, k in zip(axs.ravel(), keys):
        labels = pri[f"{k}_top"].map({True: "top", False: "lain"}).where(pri["valid"])
        map_categories(geo, ids, labels, {"top": "#b2182b", "lain": "#d9d9d9"}, f"{C.MODEL_LABELS[k.upper()]}: {nt:,} grid teratas", ax)
    save(fig, "fig_map_top10_m1_m4")

    sh = K.rank_shift(pri, "m1", "m4")
    lim = max(float(sh["shift"].abs().quantile(0.98)), 1.0)
    fig, ax = plt.subplots(figsize=(7, 6.5))
    map_grid(geo, sh["shift"].astype(float), sh[C.KEY], "Perubahan peringkat M1 ke M4 (merah = naik prioritas)", "RdBu_r", -lim, lim, ax)
    save(fig, "fig_map_rank_shift_m1_m4")

    lisa_p = paths.modeling / "lisa_m4.csv"
    if lisa_p.exists():
        lisa = pd.read_csv(lisa_p, dtype={C.KEY: str})
        fig, ax = plt.subplots(figsize=(7, 6.5))
        map_categories(geo, lisa[C.KEY], lisa["klaster_fdr"], LISA_COLORS, "LISA skor M4 (signifikan setelah koreksi FDR)", ax)
        handles = [plt.Line2D([0], [0], marker="s", ls="", color=c, label=l) for l, c in LISA_COLORS.items()]
        ax.legend(handles=handles, loc="lower left", fontsize=8, frameon=False)
        save(fig, "fig_map_lisa_m4")
    st = paths.modeling / "sensitivity_m4_stability.csv"
    if st.exists():
        stab = pd.read_csv(st, dtype={C.KEY: str})
        vals = stab["stable_share"].where(stab["baseline_top"])
        fig, ax = plt.subplots(figsize=(7, 6.5))
        map_grid(geo, vals, stab[C.KEY], "Stabilitas grid top M4 (porsi skenario sensitivitas)", "Blues", 0.0, 1.0, ax)
        save(fig, "fig_map_stability_m4")

    # ---- tabel
    v = pri.loc[pri["valid"]].merge(
        merged[[C.KEY, "lst_c", "ndvi", "population", "pop_child", "pop_elderly", "park_distance_m"]], on=C.KEY, validate="one_to_one")
    top = v.loc[v["m4_top"]].sort_values("m4_rank")
    write_csv(top[[C.KEY, "m4_rank", "m4_score", "m1_rank", "m2_rank", "m3_rank", "lst_c", "ndvi", "population",
                   "pop_child", "pop_elderly", "park_distance_m"]], paths.tables / "top10_priority_m4.csv")
    print(f"Sumber data: {meta['source'].upper()}   figur: {len(save.written)} berkas di {paths.figures}")
    print(f"Tabel: {paths.tables / 'top10_priority_m4.csv'}")
    if dummy:
        print("Semua figur ditandai DATA DUMMY. Jalankan ulang tanpa --demo setelah data asli tersedia.")


if __name__ == "__main__":
    run_cli(main)
