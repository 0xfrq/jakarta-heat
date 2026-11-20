"""Verify release-receipt hashes under the explicit Git-blob SHA-256 policy.

Policy: ``git-blob-sha256`` = SHA-256 over the bytes Git stores in the committed
blob (``git cat-file blob <rev>:<path>``), not over the platform-dependent
checkout representation.  This is the convention used by the RC1 receipt; the
same LF blobs reproduce the same digest on Windows, Linux and a fresh clone.

The verifier supports the RC1 receipt shape (named report/handoff fields) and
the RC2 receipt shape (an explicit ``entries`` list).  It never rewrites the
receipt or the candidate files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RC1_KEYS = (
    ("tests", ("tests", "report")),
    ("replay", ("replay", "report")),
    ("browser", ("browser", "report")),
    ("postbuild", ("postbuild", "report")),
    ("verification", ("independent_verification", "report")),
    ("release_gate", ("release_gate", "report")),
    ("handoff", ("handoff",)),
    ("verification_record", ("verification_record",)),
    ("integration_manifest", ("integration_manifest",)),
)


def _dig(item, keys):
    for key in keys:
        item = item[key]
    return item


def receipt_entries(receipt: dict) -> list[dict]:
    if "entries" in receipt:
        return [{"name": e["name"], "path": e["path"], "sha256": e["sha256"]} for e in receipt["entries"]]
    entries = []
    for name, keys in RC1_KEYS:
        item = _dig(receipt, keys)
        entries.append({"name": name, "path": item["path"], "sha256": item["sha256"]})
    return entries


def blob_digest(rev: str, path: str) -> str:
    data = subprocess.check_output(["git", "-C", str(ROOT), "cat-file", "blob", f"{rev}:{path}"])
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--rev", default="HEAD", help="Git revision whose blobs are bound by the receipt")
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()

    receipt_path = args.receipt if args.receipt.is_absolute() else ROOT / args.receipt
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    entries = receipt_entries(receipt)
    report = {
        "policy": "git-blob-sha256",
        "policy_definition": "SHA-256 over git cat-file blob <rev>:<path> bytes; checkout line endings are irrelevant",
        "receipt": str(receipt_path.relative_to(ROOT)) if receipt_path.is_relative_to(ROOT) else str(receipt_path),
        "revision": args.rev,
        "core_autocrlf": subprocess.run(["git", "-C", str(ROOT), "config", "--get", "core.autocrlf"],
                                         capture_output=True, text=True).stdout.strip() or "unset",
        "entries": [],
        "matched": 0,
        "mismatched": 0,
        "ok": True,
    }
    for entry in entries:
        try:
            actual = blob_digest(args.rev, entry["path"])
            error = None
        except subprocess.CalledProcessError:
            actual, error = None, "blob_not_found"
        match = actual == entry["sha256"]
        report["entries"].append({**entry, "actual_sha256": actual, "match": match, "error": error})
        report["matched" if match else "mismatched"] += 1
        report["ok"] = report["ok"] and match
        print(f"{entry['name']:22s} match={match} path={entry['path']}")
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"policy={report['policy']} rev={args.rev} matched={report['matched']}/{len(entries)} ok={report['ok']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
