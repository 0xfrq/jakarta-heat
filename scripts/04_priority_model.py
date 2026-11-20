"""Job 6A: empat model prioritas panas (M1-M4) -> modeling/priority_models.csv

    python scripts/04_priority_model.py            # data asli (butuh 03_prepare_model.py --merge)
    python scripts/04_priority_model.py --demo     # data dummy
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jhim import config as C  # noqa: E402
from jhim import pipeline as P  # noqa: E402
from jhim.io import run_cli  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--top-frac", type=float, default=C.TOP_FRAC, help="bagian grid teratas (bawaan 0.10)")
    a = ap.parse_args()
    paths = C.Paths(demo=a.demo)
    _, meta = P.step_priority(paths, top_frac=a.top_frac)
    for m in C.MODELS:
        print(f"  {C.MODEL_LABELS[m]:50s} {C.MODEL_FORMULAS[m]}")
    print(f"Sumber data: {meta['source'].upper()}. {C.WEIGHTS_STATUS}\nTertulis: {paths.priority}")


if __name__ == "__main__":
    run_cli(main)
