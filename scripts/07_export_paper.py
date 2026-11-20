"""Job 6C: ekspor figur (PNG/SVG), tabel teratas, dan GeoPackage atribut model.

    python scripts/07_export_paper.py            # data asli -> outputs/figures, outputs/tables, outputs/gis
    python scripts/07_export_paper.py --demo     # latihan (outputs/demo/..., watermark DUMMY)
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
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--formats", nargs="+", default=["png", "svg"])
    a = ap.parse_args()
    paths = C.Paths(demo=a.demo)
    feat, _ = load_merged(paths)
    pri, meta = load_priority(paths)
    P.step_export(paths, feat, pri, meta, a.dpi, a.formats)


if __name__ == "__main__":
    run_cli(main)
