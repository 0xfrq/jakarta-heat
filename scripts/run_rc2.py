"""RC2 engineering rebuild, replay, tests, dashboard and verification.

This runner is the RC2 counterpart to scripts/run_rc1.py.  It deliberately
writes every receipt and log under outputs/qa/rc2/ so the frozen RC1 evidence
tree is never overwritten.  The analysis stage needs the read-only original
audit evidence (``--audit-root``) and the frozen processed inputs already
tracked in this candidate.  The raw WorldPop/OSM bundle is only needed for the
optional upstream stage or a full raw rebuild.

Usage:
    python scripts/run_rc2.py --stage analysis --audit-root D:\\jakarta-heat-integration\\audit
    python scripts/run_rc2.py --stage tests
    python scripts/run_rc2.py --stage browser
    python scripts/run_rc2.py --stage verify --audit-root D:\\jakarta-heat-integration\\audit
    python scripts/run_rc2.py --stage all --audit-root D:\\jakarta-heat-integration\\audit
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/qa/rc2"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", choices=("analysis", "tests", "browser", "verify", "all"), default="all")
    ap.add_argument("--audit-root", type=Path, default=None,
                    help="Read-only original audit evidence (required for analysis/verify)")
    ap.add_argument("--source-root", type=Path, default=None,
                    help="Read-only restored frozen-input root for source-manifest hash checks")
    ap.add_argument("--skip-replay", action="store_true", help="Run the remediation once; do not claim replay")
    args = ap.parse_args()
    if args.stage in ("analysis", "verify", "all") and args.audit_root is None:
        ap.error("--audit-root is required for analysis/verify; raw acquisition evidence is not in Git")
    if args.stage in ("analysis", "verify", "all") and not Path(args.audit_root).is_dir():
        ap.error(f"--audit-root does not exist: {args.audit_root}")

    OUT.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8", "MPLBACKEND": "Agg"}
    for key in list(env):
        if key.startswith("JHIM_"):
            del env[key]

    def run(name: str, *cmd: str) -> None:
        print(f"RC2 {name}", flush=True)
        log = OUT / f"{name}.log"
        with log.open("w", encoding="utf-8") as stream:
            result = subprocess.run([sys.executable, *cmd], cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
        receipt = {"command": [Path(sys.executable).name, *cmd], "returncode": result.returncode,
                   "finished_utc": datetime.now(timezone.utc).isoformat(),
                   "log": log.relative_to(ROOT).as_posix()}
        (OUT / f"{name}.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        if result.returncode:
            print(log.read_text(encoding="utf-8")[-12000:], flush=True)
            raise SystemExit(result.returncode)

    if args.stage in ("analysis", "all"):
        run("input_status", "scripts/run_agent3_pipeline.py", "--status")
        run("remediation_run1", "scripts/run_agent3_remediation.py", "--integrated", "--audit", str(args.audit_root))
        if not args.skip_replay:
            run("capture", "scripts/check_agent3_replay.py", "--capture",
                "--snapshot", "outputs/qa/rc2/replay_snapshot",
                "--report", "outputs/qa/rc2/replay_verification.json")
            run("remediation_run2", "scripts/run_agent3_remediation.py", "--integrated", "--audit", str(args.audit_root))
            run("replay", "scripts/check_agent3_replay.py",
                "--snapshot", "outputs/qa/rc2/replay_snapshot",
                "--report", "outputs/qa/rc2/replay_verification.json")
        run("pipeline", "scripts/run_agent3_pipeline.py")
        run("p2_diagnostics", "scripts/run_agent3_pipeline.py", "--p2-only")
    if args.stage in ("tests", "all"):
        run("tests", "-m", "pytest", "-q", "-ra", "-p", "no:cacheprovider", "tests",
            "--junitxml=outputs/qa/rc2/pytest.xml")
    if args.stage in ("browser", "all"):
        run("browser", "scripts/check_agent3_dashboard.py", "--integrated",
            "--output-dir", "outputs/qa/rc2/dashboard",
            "--scope", "RC2 canonical inputs; provisional scientific policy")
    if args.stage in ("verify", "all"):
        verify_cmd = ["scripts/verify_rc2.py", "--audit-root", str(args.audit_root)]
        if args.source_root is not None:
            verify_cmd += ["--source-root", str(args.source_root)]
        run("verification", *verify_cmd)
    return 0


if __name__ == "__main__":
    sys.exit(main())
