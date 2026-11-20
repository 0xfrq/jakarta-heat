"""Pipeline analisis Agent 3 / Person 3 (satu perintah).

    python scripts/run_agent3_pipeline.py --status        # hanya periksa status masukan
    python scripts/run_agent3_pipeline.py --p2-only       # diagnostik data Person 2 (tanpa remote sensing)
    python scripts/run_agent3_pipeline.py                 # pipeline model lengkap (butuh remote_sensing_grid.csv)
    python scripts/run_agent3_pipeline.py --demo          # latihan dengan data dummy (folder demo, watermark)

Kode keluar: 0 = sukses, 2 = masukan hulu belum tersedia (bukan galat kode), 1 = galat data/struktur.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jhim import config as C  # noqa: E402
from jhim import data as D  # noqa: E402
from jhim import pipeline as P  # noqa: E402
from jhim.util import DataError, PendingInputs, utf8_stdout  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demo", action="store_true", help="data dummy, keluaran ke folder demo")
    ap.add_argument("--status", action="store_true", help="hanya cetak status masukan")
    ap.add_argument("--p2-only", action="store_true", help="hanya diagnostik data Person 2")
    ap.add_argument("--unreachable", choices=[*C.UNREACHABLE_POLICIES, "cap"], default="exclude",
                    help="perlakuan park_distance_m kosong (baseline: exclude)")
    ap.add_argument("--perms", type=int, default=C.PERMUTATIONS)
    ap.add_argument("--skip-spatial", action="store_true")
    ap.add_argument("--skip-figures", action="store_true")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--formats", nargs="+", default=["png", "svg"])
    ap.add_argument("--force", action="store_true", help="jalan walau grid valid < 70%% (dokumentasikan!)")
    a = ap.parse_args()
    paths = C.Paths(demo=a.demo)

    st = D.assess_inputs(paths)
    print(f"Status masukan: {st.state} - {st.text}")
    for k, v in st.files.items():
        print(f"  [{'ADA' if v['exists'] else 'belum'}] {k}: {v['path']}")
    for n in st.notes:
        print("  catatan:", n)
    for e in st.errors:
        print("  GALAT:", e)
    if a.status:
        return 1 if st.state == D.INVALID else 0
    if st.state == D.INVALID:
        return 1
    if a.p2_only:
        P.step_p2_diagnostics(paths, a.perms, spatial=not a.skip_spatial)
        P.write_manifest(paths, ["p2_diagnostics"], {"runtime": {"permutations": a.perms, "seed": C.SEED,
                          "skip_spatial": a.skip_spatial}}, target=paths.qa / "run_manifest.json")
        return 0
    man = P.run_all(paths, a.unreachable, a.perms, a.skip_spatial, a.skip_figures, a.force, a.dpi, a.formats)
    print(json.dumps({k: man[k] for k in ("input_status", "steps", "source", "n_valid")}, ensure_ascii=False))
    print(f"Manifest: {paths.manifest}")
    return 0


if __name__ == "__main__":
    utf8_stdout()
    try:
        sys.exit(main())
    except PendingInputs as exc:
        print(f"\nTERTUNDA: {exc}", file=sys.stderr)
        sys.exit(2)
    except DataError as exc:
        print(f"\nGAGAL: {exc}", file=sys.stderr)
        sys.exit(1)
