"""Verify committed demographic source manifests without requiring data/raw in Git.

The manifests are checkout-portable (repository-relative POSIX paths).  The raw
WorldPop rasters are distributed in the separate frozen-input bundle and are
Git-ignored, so a clean checkout can verify the path contract but not the file
hashes.  Point ``--source-root`` at a read-only restored bundle to verify the
hashes as well; use ``--require-all`` to make a missing raster a failure.

Examples:
    python scripts/verify_source_manifests.py
    python scripts/verify_source_manifests.py --source-root D:\\frozen_inputs --require-all
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from aggregate_demographics import verify_manifest  # noqa: E402

DEFAULT_MANIFESTS = (
    "outputs/qa/remediation_agent2/demographic_source_manifest.json",
    "outputs/qa/remediation_agent2/original_masks/demographic_source_manifest.json",
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", action="append", default=[], help="Manifest to verify (repeatable)")
    ap.add_argument("--root", type=Path, default=ROOT, help="Candidate checkout root")
    ap.add_argument("--source-root", type=Path, default=None, help="Read-only restored frozen-input root")
    ap.add_argument("--require-all", action="store_true", help="Fail when any raw source is absent")
    ap.add_argument("--json-out", type=Path, default=None, help="Write the complete report here")
    args = ap.parse_args()

    manifests = args.manifest or list(DEFAULT_MANIFESTS)
    report = {"policy": "repository-relative POSIX paths; SHA-256 over exact source bytes",
              "root": str(args.root.resolve()),
              "source_root": str(args.source_root.resolve()) if args.source_root else None,
              "manifests": {}, "ok": True}
    for rel in manifests:
        path = args.root / rel
        items = json.loads(path.read_text(encoding="utf-8"))
        result = verify_manifest(items, args.root, args.source_root, require_all=args.require_all)
        report["manifests"][rel] = result
        report["ok"] = report["ok"] and result["ok"]
        print(f"{rel}: checked={result['checked']} existing={result['existing']} "
              f"matched={result['matched']} missing={len(result['missing'])} "
              f"mismatches={len(result['mismatches'])} ok={result['ok']}")
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
