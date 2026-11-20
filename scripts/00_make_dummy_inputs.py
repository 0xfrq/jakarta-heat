"""Buat data dummy dari master grid ASLI agar Job 6A-6C bisa dilatih sebelum data Orang 1 dan 2 tiba.

Keluaran ditulis ke data/processed/dummy/ (terpisah dari data asli) dan memuat kolom is_dummy=1.
    python scripts/00_make_dummy_inputs.py
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jhim import config as C  # noqa: E402
from jhim.data import read_grid_table  # noqa: E402
from jhim.dummy import make_dummy_inputs  # noqa: E402
from jhim.io import run_cli  # noqa: E402
from jhim.util import write_csv  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grid", default=None, help="master grid (.gpkg); bawaan data/processed/grid_500m_jakarta.gpkg")
    ap.add_argument("--seed", type=int, default=C.SEED)
    a = ap.parse_args()
    paths = C.Paths(demo=True)
    grid = read_grid_table(a.grid or paths.grid)
    rs, pop = make_dummy_inputs(grid, a.seed)
    write_csv(rs, paths.rs)
    write_csv(pop, paths.pop)
    print(f"Grid master      : {len(grid):,}")
    print(f"Tertulis (DUMMY) : {paths.rs}  ({len(rs):,} baris)")
    print(f"Tertulis (DUMMY) : {paths.pop}  ({len(pop):,} baris)")
    print("Data ini sintetis. Jangan dipakai untuk hasil paper.")


if __name__ == "__main__":
    run_cli(main)
