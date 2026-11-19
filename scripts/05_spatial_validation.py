"""Job 6B: perbandingan model (Spearman, Jaccard, perubahan peringkat, cakupan penduduk)
dan uji pola spasial (Moran global, LISA).

    python scripts/05_spatial_validation.py             # data asli
    python scripts/05_spatial_validation.py --demo
    python scripts/05_spatial_validation.py --skip-spatial   # hanya perbandingan (tanpa libpysal)
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

from jhim import compare as K  # noqa: E402
from jhim import config as C  # noqa: E402
from jhim import spatial as SP  # noqa: E402
from jhim.data import read_grid_gdf  # noqa: E402
from jhim.io import load_merged, load_priority, run_cli  # noqa: E402
from jhim.util import DataError, write_csv, write_json  # noqa: E402


def comparison(paths, merged, pri):
    keys = K.model_keys(pri)
    sp, ja = K.spearman_matrix(pri, keys), K.jaccard_matrix(pri, keys)
    write_csv(K.pairwise_long(pri, keys), paths.tables / "model_comparison.csv")
    write_csv(sp.reset_index(names="model"), paths.tables / "spearman_matrix.csv")
    write_csv(ja.reset_index(names="model"), paths.tables / "jaccard_matrix.csv")
    cov = K.top_coverage(pri, merged, keys)
    write_csv(cov, paths.tables / "model_top10_coverage.csv")
    shift = K.rank_shift(pri, "m1", "m4")
    write_csv(shift, paths.modeling / "rank_shift_m1_m4.csv")
    print("Spearman antar skor:\n", sp.round(3).to_string())
    print("\nJaccard 10% teratas:\n", ja.round(3).to_string())
    print("\nCakupan 10% teratas:")
    with pd.option_context("display.width", 160):
        print(cov[["kelompok", "n_grid", "pct_populasi_valid", "pct_rentan_valid", "lst_rata2",
                   "jarak_taman_median_m", "pct_grid_taman_lebih_500m"]].round(1).to_string(index=False))
    print("\nTransisi M1 -> M4:\n", shift["transisi"].value_counts().to_string())


def spatial(paths, pri, lisa_model: str, perms: int):
    g = read_grid_gdf(paths.grid)
    v = pri.loc[pri["valid"]]
    sub = g[g[C.KEY].isin(v[C.KEY])].reset_index(drop=True)
    sub = sub.merge(v, on=C.KEY, how="left", validate="one_to_one")
    if len(sub) != len(v):
        raise DataError("Geometri master grid tidak cocok dengan grid valid.")
    w = SP.queen_weights(sub)
    print(f"\nBobot Queen: {len(sub):,} grid, pulau (tanpa tetangga): {len(w.islands)}")
    rows = []
    for k in K.model_keys(pri):
        r = SP.global_moran(sub[f"{k}_score"], w, perms)
        rows.append({"model": k.upper(), **r})
    gm = pd.DataFrame(rows)
    write_csv(gm, paths.tables / "moran_global.csv")
    print("Moran global (Queen, baris-standar):")
    print(gm[["model", "I", "z_sim", "p_sim", "n_islands"]].round(4).to_string(index=False))

    lk = lisa_model.lower()
    lisa = SP.local_moran(sub[f"{lk}_score"], w, perms)
    lisa.insert(0, C.KEY, sub[C.KEY].to_numpy())
    write_csv(lisa, paths.modeling / f"lisa_{lk}.csv")
    cnt = pd.crosstab(lisa["klaster_p05"], lisa["klaster_fdr"])
    print(f"\nLISA {lisa_model.upper()}: klaster signifikan p<0.05 vs setelah koreksi FDR")
    print(cnt.to_string())
    write_json(paths.tables / "spatial_validation_info.json", {
        "weights": "Queen contiguity, row-standardized", "permutations": perms, "seed": C.SEED,
        "lisa_model": lisa_model.upper(), "alpha": C.LISA_ALPHA, "n_islands": len(w.islands),
        "catatan": "LISA diuji berkali-kali; gunakan kolom klaster_fdr (Benjamini-Hochberg) untuk klaim.",
    })


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--skip-spatial", action="store_true", help="lewati Moran/LISA (tanpa geopandas/libpysal)")
    ap.add_argument("--lisa-model", default="M4", choices=list(C.MODELS))
    ap.add_argument("--perms", type=int, default=C.PERMUTATIONS)
    a = ap.parse_args()
    paths = C.Paths(demo=a.demo)
    merged, _ = load_merged(paths)
    pri, meta = load_priority(paths)
    print(f"Sumber data: {meta['source'].upper()}")
    comparison(paths, merged, pri)
    if not a.skip_spatial:
        spatial(paths, pri, a.lisa_model, a.perms)
    print(f"\nTabel tertulis di: {paths.tables}")


if __name__ == "__main__":
    run_cli(main)
