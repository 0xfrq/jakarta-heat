"""Job 4A (uji master grid) dan awal Job 6A (gabung data).

    python scripts/03_prepare_model.py                     # 4A: uji master grid dan cek berkas
    python scripts/03_prepare_model.py --merge             # 6A: gabung data ASLI -> modeling/merged_grid.csv
    python scripts/03_prepare_model.py --merge --demo      # latihan memakai data dummy (folder terpisah)
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

from jhim import config as C  # noqa: E402
from jhim import data  # noqa: E402
from jhim.io import run_cli  # noqa: E402
from jhim.util import DataError, write_csv, write_json  # noqa: E402


def check_grid(paths: C.Paths):
    """Job 4A: uji master grid (sama semangatnya dengan roadmap, tahan terhadap layer/nama geometri berbeda)."""
    try:
        import geopandas as gpd
    except ImportError as exc:
        raise DataError("geopandas belum terpasang: python -m pip install geopandas") from exc
    p = paths.grid
    if not p.exists():
        raise DataError(f"Master grid tidak ditemukan: {p}")
    try:
        print("Layer di berkas:\n", gpd.list_layers(p).to_string(index=False))
    except Exception:
        pass
    grid = data.read_grid_gdf(p)  # memilih layer yang punya geometri + grid_id; CRS wajib ada
    assert grid[C.KEY].notna().all(), "Ada grid_id kosong"
    assert grid[C.KEY].is_unique, "Ada grid_id duplikat"
    print("Jumlah grid  :", len(grid))
    print("CRS          :", grid.crs)
    print(grid[[C.KEY]].head())
    area_km2 = grid.to_crs("EPSG:32748").area / 1e6
    print(f"Luas grid    : median {area_km2.median():.3f} km2 (500 m x 500 m = 0.250); min {area_km2.min():.3f}; maks {area_km2.max():.3f}")
    print("\nStatus berkas dari rekan:")
    for label, f in (("Orang 1", paths.rs), ("Orang 2 (gabungan)", paths.pop),
                     *[("Orang 2 (terpisah)", q) for q in paths.pop_parts]):
        print(f"  [{'ADA' if f.exists() else 'belum'}] {label}: {f}")
    print("\nLULUS Job 4A: grid terbaca, CRS terdeteksi, grid_id tidak kosong dan unik.")


def merge(paths: C.Paths, unreachable: str, grid_path=None):
    grid = data.read_grid_table(grid_path or paths.grid)
    rs = data.read_input_csv(paths.rs, C.RS_COLS, "remote_sensing_grid.csv")
    pop, pop_notes = data.load_population_inputs(paths)
    merged, notes, dummy = data.merge_inputs(grid[C.KEY], rs, pop)
    notes = pop_notes + notes
    if dummy and not paths.demo:
        notes.append("PERINGATAN: berkas masukan memuat is_dummy=1 walau mode asli; hasil ditandai dummy.")
    clean = data.clean_values(merged, unreachable)
    meta = data.build_meta(clean, notes, dummy or paths.demo, unreachable)
    q = data.quality_table(clean)

    write_csv(clean, paths.merged)
    write_json(paths.merged_meta, meta)
    write_csv(q, paths.tables / "data_quality.csv")

    print(f"Sumber data : {meta['source'].upper()}")
    print(f"Grid master : {meta['n_grid']:,}   valid: {meta['n_valid']:,} ({meta['valid_share']:.1%})")
    print("\nTabel kualitas data:")
    with pd.option_context("display.width", 120, "display.max_colwidth", 60):
        print(q.to_string(index=False))
    for n in notes:
        print("Catatan:", n)
    if meta["valid_share"] < 0.7:
        print("\nPERINGATAN: kurang dari 70% grid valid. Laporkan ke Orang 1/2 sebelum memodelkan.")
    print(f"\nTertulis: {paths.merged}\nTertulis: {paths.merged_meta}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--merge", action="store_true", help="gabung data (6A); tanpa ini hanya uji master grid (4A)")
    ap.add_argument("--demo", action="store_true", help="pakai data dummy dan folder keluaran terpisah")
    ap.add_argument("--unreachable", choices=["exclude", "cap"], default="exclude",
                    help="taman tak terjangkau (park_distance_m kosong): exclude=keluarkan grid (bawaan), cap=isi batas 1000 m")
    ap.add_argument("--grid", default=None, help="jalur master grid lain (.gpkg; .csv hanya untuk uji)")
    a = ap.parse_args()
    paths = C.Paths(demo=a.demo)
    if a.merge:
        merge(paths, a.unreachable, a.grid)
    else:
        check_grid(paths)


if __name__ == "__main__":
    run_cli(main)
