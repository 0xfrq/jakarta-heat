"""Job 6B: uji sensitivitas stabilitas 10% grid prioritas teratas.

Skenario: bobot tiap komponen x0.8 dan x1.2 (dinormalisasi ulang), ambang akses taman biner 500 m dan
1000 m, normalisasi min-max murni, dan pemotongan persentil 1-99.

    python scripts/06_sensitivity.py [--demo] [--model M4]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

from jhim import config as C  # noqa: E402
from jhim import sensitivity as SE  # noqa: E402
from jhim.io import load_merged, run_cli  # noqa: E402
from jhim.util import write_csv, write_json  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--model", default="M4", choices=list(C.MODELS))
    a = ap.parse_args()
    paths = C.Paths(demo=a.demo)
    merged, meta = load_merged(paths)
    summ, stab, info = SE.run_sensitivity(merged, a.model)
    info["source"] = meta["source"]
    k = a.model.lower()
    write_csv(summ, paths.tables / f"sensitivity_{k}_summary.csv")
    write_csv(stab, paths.modeling / f"sensitivity_{k}_stability.csv")
    write_json(paths.tables / f"sensitivity_{k}_info.json", info)
    print(f"Sumber data: {meta['source'].upper()}   model: {a.model}   skenario: {info['n_scenarios']}")
    with pd.option_context("display.width", 140):
        print(summ.round(3).to_string(index=False))
    print(
        f"\nDari {info['n_top']:,} grid top: {info['n_baseline_top_stable']:,} "
        f"({info['share_baseline_top_stable']:.0%}) masuk top di >= {C.STABLE_SHARE:.0%} skenario; "
        f"{info['n_baseline_top_in_all']:,} masuk top di SEMUA skenario. Jaccard terendah {info['min_jaccard']:.2f}."
    )
    print("Jangan menyebut hasil 'robust' kecuali angka di atas mendukung; laporkan apa adanya.")


if __name__ == "__main__":
    run_cli(main)
