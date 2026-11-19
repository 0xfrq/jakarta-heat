"""Job 6A: empat model prioritas panas (M1-M4) -> modeling/priority_models.csv

    python scripts/04_priority_model.py            # data asli
    python scripts/04_priority_model.py --demo     # data dummy
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jhim import config as C  # noqa: E402
from jhim import models as M  # noqa: E402
from jhim.io import load_merged, run_cli  # noqa: E402
from jhim.util import utc_stamp, write_csv, write_json  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--top-frac", type=float, default=C.TOP_FRAC, help="bagian grid teratas (bawaan 0.10)")
    a = ap.parse_args()
    paths = C.Paths(demo=a.demo)
    merged, mmeta = load_merged(paths)
    pri = M.build_priority_table(merged, top_frac=a.top_frac)
    write_csv(pri, paths.priority)
    nv = int(pri["valid"].sum())
    meta = {
        "source": mmeta["source"],
        "built_at": utc_stamp(),
        "n_grid": int(len(pri)),
        "n_valid": nv,
        "top_frac": a.top_frac,
        "n_top": M.n_top(nv, a.top_frac),
        "models": C.MODELS,
        "norm_clip": list(C.NORM_CLIP),
        "park_cap_m": C.PARK_CAP_M,
        "unreachable_policy": mmeta.get("unreachable_policy"),
        "rank_rule": "rank 1 = prioritas tertinggi; seri dipecah oleh skor tanpa pemotongan lalu grid_id",
    }
    write_json(paths.priority_meta, meta)
    print(f"Sumber data: {meta['source'].upper()}   grid valid: {nv:,}   top {a.top_frac:.0%} = {meta['n_top']:,} grid")
    for m, w in C.MODELS.items():
        k = m.lower()
        print(f"  {C.MODEL_LABELS[m]:55s} bobot {w}")
        top = pri.loc[pri[f'{k}_rank'] == 1, C.KEY].iloc[0]
        print(f"      grid peringkat 1: {top}")
    print(f"\nTertulis: {paths.priority}")


if __name__ == "__main__":
    run_cli(main)
