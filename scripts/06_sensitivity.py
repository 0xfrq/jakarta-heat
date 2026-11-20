"""Job 6B: uji sensitivitas (eksploratif, one-at-a-time) untuk M2, M3, M4.

    python scripts/06_sensitivity.py [--demo] [--model M4 ...]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jhim import config as C  # noqa: E402
from jhim import pipeline as P  # noqa: E402
from jhim.io import load_merged, run_cli  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--model", nargs="+", default=["M2", "M3", "M4"], choices=list(C.MODELS))
    a = ap.parse_args()
    paths = C.Paths(demo=a.demo)
    feat, _ = load_merged(paths)
    P.step_sensitivity(paths, feat, tuple(a.model))
    print("Jangan menyebut hasil 'robust' kecuali metrik mendukung; laporkan apa adanya.")


if __name__ == "__main__":
    run_cli(main)
