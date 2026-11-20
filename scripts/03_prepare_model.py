"""Job 4A (uji master grid + status masukan) dan awal Job 6A (gabung data).

    python scripts/03_prepare_model.py                     # 4A: uji master grid dan status masukan
    python scripts/03_prepare_model.py --merge             # 6A: gabung data ASLI -> modeling/merged_grid.csv
    python scripts/03_prepare_model.py --merge --demo      # latihan memakai data dummy (folder terpisah)

Pembungkus tipis atas jhim.pipeline (scripts/run_agent3_pipeline.py menjalankan semua langkah sekaligus).
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jhim import config as C  # noqa: E402
from jhim import data  # noqa: E402
from jhim import pipeline as P  # noqa: E402
from jhim.io import run_cli  # noqa: E402


def check_grid(paths: C.Paths):
    grid = data.read_grid_gdf(paths.grid, attrs=True)
    area_km2 = grid.to_crs(C.CRS_PROJECTED).area / 1e6
    print("Jumlah grid  :", len(grid), f"(diharapkan {C.EXPECTED_N_GRID})")
    print("CRS          :", grid.crs)
    print(f"Luas grid    : median {area_km2.median():.3f} km2; min {area_km2.min():.5f}; maks {area_km2.max():.3f}")
    st = data.assess_inputs(paths)
    print(f"\nStatus masukan: {st.state} - {st.text}")
    for k, v in st.files.items():
        print(f"  [{'ADA' if v['exists'] else 'belum'}] {k}: {v['path']}")
    for n in st.notes + st.errors:
        print("  -", n)
    print("\nLULUS Job 4A: grid terbaca, CRS terdeteksi, grid_id tidak kosong dan unik.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--merge", action="store_true", help="gabung data (6A); tanpa ini hanya uji master grid (4A)")
    ap.add_argument("--demo", action="store_true", help="pakai data dummy dan folder keluaran terpisah")
    ap.add_argument("--unreachable", choices=[*C.UNREACHABLE_POLICIES, "cap"], default="exclude",
                    help="park_distance_m kosong: exclude (bawaan) / worst / median")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    paths = C.Paths(demo=a.demo)
    if a.merge:
        feat, _ = P.step_merge(paths, a.unreachable, a.force)
        print(data.quality_table(feat).to_string(index=False))
    else:
        check_grid(paths)


if __name__ == "__main__":
    run_cli(main)
