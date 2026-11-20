"""Job 6B: perbandingan model (Spearman, Kendall, Jaccard, transisi, kota) dan Moran global / LISA.

    python scripts/05_spatial_validation.py             # data asli
    python scripts/05_spatial_validation.py --demo
    python scripts/05_spatial_validation.py --skip-spatial   # hanya perbandingan
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jhim import config as C  # noqa: E402
from jhim import pipeline as P  # noqa: E402
from jhim.io import load_merged, load_priority, run_cli  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--skip-spatial", action="store_true")
    ap.add_argument("--perms", type=int, default=C.PERMUTATIONS)
    a = ap.parse_args()
    paths = C.Paths(demo=a.demo)
    feat, _ = load_merged(paths)
    pri, meta = load_priority(paths)
    print(f"Sumber data: {meta['source'].upper()}")
    P.step_compare(paths, feat, pri)
    if not a.skip_spatial:
        P.step_spatial(paths, feat, pri, a.perms)


if __name__ == "__main__":
    run_cli(main)
