"""RC2 portability verification: receipts, relative manifests, source hashes and paths.

Hash policy
-----------
``git-blob-sha256`` is SHA-256 over ``git cat-file blob <rev>:<path>``.  This is
the portable identity used by the RC1 receipt; the three RC1 entries that fail
on a Windows checkout do so only because ``core.autocrlf`` rewrites LF blobs to
CRLF.  The committed blob is unchanged and is what the receipt binds.

Output manifests use exact-file SHA-256 and repository-relative POSIX paths.
``data/**`` and ``outputs/**`` are ``-text`` in ``.gitattributes`` so checkout
bytes are stable.

Usage:
    python scripts/verify_portability.py --source-root D:\\jakarta-heat-integration --allow-missing-rc2
    python scripts/verify_portability.py --source-root D:\\jakarta-heat-integration
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from aggregate_demographics import verify_manifest  # noqa: E402
from verify_receipt_hashes import blob_digest, receipt_entries  # noqa: E402

OUT = ROOT / "outputs/qa/rc2"
RC1_REV = "3b8ed05be92c35bbb2b3a617688540ee856b11c8"
MANIFESTS = (
    "data/processed/modeling/output_sha256_manifest.csv",
    "data/processed/modeling_remediation/output_sha256_manifest.csv",
)
SOURCE_MANIFESTS = (
    "outputs/qa/remediation_agent2/demographic_source_manifest.json",
    "outputs/qa/remediation_agent2/original_masks/demographic_source_manifest.json",
)


def disk_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt_report(receipt_rel: str, rev: str) -> dict:
    receipt = json.loads((ROOT / receipt_rel).read_text(encoding="utf-8"))
    entries = receipt_entries(receipt)
    rows = []
    for entry in entries:
        actual = blob_digest(rev, entry["path"])
        rows.append({**entry, "actual_sha256": actual, "match": actual == entry["sha256"]})
    return {"receipt": receipt_rel, "revision": rev, "policy": "git-blob-sha256",
            "entries": rows, "matched": sum(r["match"] for r in rows), "total": len(rows),
            "ok": all(r["match"] for r in rows)}


def disk_byte_before_after(receipt_rel: str) -> dict:
    """Document the RC1 Windows-checkout symptom without rewriting any file."""
    receipt = json.loads((ROOT / receipt_rel).read_text(encoding="utf-8"))
    rows = []
    for entry in receipt_entries(receipt):
        p = ROOT / entry["path"]
        actual = disk_digest(p)
        crlf = p.read_bytes().count(b"\r\n")
        rows.append({"name": entry["name"], "path": entry["path"], "expected_blob_sha256": entry["sha256"],
                     "disk_sha256": actual, "disk_match": actual == entry["sha256"],
                     "crlf_pairs": crlf, "lf": p.read_bytes().count(b"\n")})
    return {"receipt": receipt_rel, "entries": rows,
            "disk_matches": sum(r["disk_match"] for r in rows), "total": len(rows),
            "note": "Disk-byte mismatches on Windows are line-ending conversion, not changed Git blobs."}


def output_manifest_report(rel: str) -> dict:
    rows = []
    for line in (ROOT / rel).read_text(encoding="utf-8").splitlines()[1:]:
        path, digest = line.rsplit(",", 1)
        rows.append((path, digest))
    absolute = [p for p, _ in rows if ":" in p or p.startswith("/")]
    missing, mismatch = [], []
    for path, digest in rows:
        target = ROOT / path
        if not target.is_file():
            missing.append(path)
        elif disk_digest(target) != digest:
            mismatch.append(path)
    return {"manifest": rel, "entries": len(rows), "absolute_paths": absolute,
            "missing": missing, "hash_mismatches": mismatch,
            "ok": not absolute and not missing and not mismatch}


def source_manifest_report(source_root: Path | None) -> dict:
    manifests = {}
    for rel in SOURCE_MANIFESTS:
        items = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        manifests[rel] = verify_manifest(items, ROOT, source_root, require_all=source_root is not None)
    return {"manifests": manifests, "source_root": str(source_root) if source_root else None,
            "ok": all(m["ok"] for m in manifests.values())}


def path_scan() -> dict:
    files = ["docs/integration_manifest.json", "docs/RC2_BUILD_RECORD.json",
             "data/processed/modeling/run_manifest.json",
             "data/processed/modeling_remediation/run_manifest.json"]
    findings = {}
    for rel in files:
        p = ROOT / rel
        if not p.is_file():
            findings[rel] = {"exists": False, "absolute_paths": [], "ok": False}
            continue
        text = p.read_text(encoding="utf-8")
        absolute = [token for token in ("D:\\", "C:\\", "/home/", "/Users/") if token in text]
        findings[rel] = {"exists": True, "absolute_path_markers": absolute, "ok": not absolute}
    return {"files": findings, "ok": all(v["ok"] for v in findings.values())}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source-root", type=Path, default=None,
                    help="Read-only restored frozen-input root for source-manifest hash checks")
    ap.add_argument("--rc1-receipt", default="handoff/RC1_CANDIDATE_RECEIPT.json")
    ap.add_argument("--rc2-receipt", default="handoff/RC2_CANDIDATE_RECEIPT.json")
    ap.add_argument("--rev", default="HEAD")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    rc1 = receipt_report(args.rc1_receipt, RC1_REV)
    # The RC2 receipt binds this report, so checking it here would create a
    # circular hash dependency.  It is verified separately after the receipt
    # commit; that report is not itself receipt-bound.
    rc2 = {"receipt": args.rc2_receipt, "revision": args.rev, "policy": "git-blob-sha256",
           "status": "verified_separately",
           "report": "outputs/qa/rc2/rc2_receipt_hash_check.json"}
    reports = {
        "policy": {
            "name": "git-blob-sha256",
            "definition": "SHA-256 over git cat-file blob <rev>:<path> bytes; checkout line endings are irrelevant",
            "output_manifest": "exact-file SHA-256 with repository-relative POSIX paths; data/** and outputs/** are -text",
            "rationale": "The RC1 receipt expected hashes are canonical LF blobs; three Windows disk checks failed only because core.autocrlf=true.",
        },
        "core_autocrlf": subprocess.run(["git", "-C", str(ROOT), "config", "--get", "core.autocrlf"],
                                         capture_output=True, text=True).stdout.strip() or "unset",
        "rc1_receipt": rc1,
        "rc2_receipt": rc2,
        "rc1_disk_byte_check": disk_byte_before_after(args.rc1_receipt),
        "output_manifests": {rel: output_manifest_report(rel) for rel in MANIFESTS},
        "source_manifests": source_manifest_report(args.source_root),
        "path_scan": path_scan(),
    }
    checks = {
        "rc1_receipt_9_of_9_git_blobs": rc1["ok"],
        "standard_output_manifest_69": reports["output_manifests"][MANIFESTS[0]]["entries"] == 69
                                       and reports["output_manifests"][MANIFESTS[0]]["ok"],
        "remediation_output_manifest_80": reports["output_manifests"][MANIFESTS[1]]["entries"] == 80
                                            and reports["output_manifests"][MANIFESTS[1]]["ok"],
        "source_manifests_portable": reports["source_manifests"]["ok"],
        "current_manifests_no_absolute_paths": reports["path_scan"]["ok"],
    }
    result = "PASS" if all(checks.values()) else "FAIL"
    reports["checks"] = checks
    reports["result"] = result
    (OUT / "portability_verification.json").write_text(json.dumps(reports, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"result": result, "checks": checks,
                      "rc1_receipt": f"{rc1['matched']}/{rc1['total']}",
                      "rc2_receipt": rc2["status"],
                      "outputs": {k: f"{v['entries']} entries, ok={v['ok']}" for k, v in reports["output_manifests"].items()}},
                     indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
