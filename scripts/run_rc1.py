"""Consolidated offline RC1 rebuild, tests and review evidence from local frozen inputs."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/qa/rc1"

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", choices=("upstream", "analysis", "tests", "browser", "verify", "all"), default="all")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8", "MPLBACKEND": "Agg"}
    for k in list(env):
        if k.startswith("JHIM_"):
            del env[k]
    def run(name, *cmd, receipt=None):
        print(f"RC1 {name}", flush=True)
        log = OUT / f"{name}.log"
        with log.open("w", encoding="utf-8") as f:
            result = subprocess.run([sys.executable, *cmd], cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT)
        record = {"command": [sys.executable, *cmd], "returncode": result.returncode,
                  "finished_utc": datetime.now(timezone.utc).isoformat(), "log": str(log.relative_to(ROOT))}
        receipt_path = OUT / (receipt or f"{name}.json")
        receipt_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        if result.returncode:
            print(log.read_text(encoding="utf-8")[-10000:], flush=True)
            raise SystemExit(result.returncode)
    if args.stage in ("upstream", "all"):
        run("pip_check", "-m", "pip", "check")
        run("frozen_inputs", "scripts/agent2_freeze_inputs.py")
        man = json.loads((ROOT / "docs/remote_sensing_export_manifest.json").read_text())
        for item in man["original_exports"]:
            assert hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"], item["path"]
        run("remote_sensing", "scripts/02b_aggregate_remote_sensing.py", "--output-dir", "data/processed/remote_sensing_remediated")
        run("remote_sensing_qa", "scripts/02d_validate_remote_sensing.py", "--rs-dir", "data/processed/remote_sensing_remediated", "--output-dir", "outputs/qa/rc1/remote_sensing")
        common = ["scripts/aggregate_demographics.py", "--population", "data/raw/worldpop/idn_pop_2024.tif"]
        run("demographics_original", *common, "--pop-child", "data/raw/worldpop/age/jakarta_child_2024.tif",
            "--pop-elderly", "data/raw/worldpop/age/jakarta_elderly_2024.tif", "--support-version", "agent2-DM-01-v1-original-masks",
            "--output-dir", "outputs/qa/remediation_agent2/original_masks", "--qa-dir", "outputs/qa/remediation_agent2/original_masks")
        run("demographics_corrected", *common, "--pop-child", "data/raw/worldpop/age_buffered/jakarta_child_2024_buffered.tif",
            "--pop-elderly", "data/raw/worldpop/age_buffered/jakarta_elderly_2024_buffered.tif", "--support-version", "agent2-DM-01-v1-buffered-age")
        run("spatial_integration", "scripts/07_integrate_spatial.py", "--demographics", "data/processed/demographic_features_corrected.csv",
            "--support", "data/processed/demographic_support.csv")
        run("parks", "scripts/agent2_park_evidence.py")
        run("connectors", "scripts/agent2_connector_remediation.py")
        run("gis_effects", "scripts/agent2_remediation_effects.py")
        run("demo_inputs", "scripts/00_make_dummy_inputs.py")
    if args.stage in ("analysis", "all"):
        run("input_status", "scripts/run_agent3_pipeline.py", "--status")
        run("remediation_run1", "scripts/run_agent3_remediation.py", "--integrated", "--audit", "audit")
        run("capture", "scripts/check_agent3_replay.py", "--capture")
        run("remediation_run2", "scripts/run_agent3_remediation.py", "--integrated", "--audit", "audit")
        run("replay", "scripts/check_agent3_replay.py")
        run("pipeline", "scripts/run_agent3_pipeline.py")
        run("p2_diagnostics", "scripts/run_agent3_pipeline.py", "--p2-only")
    if args.stage in ("tests", "all"):
        run("tests", "-m", "pytest", "-q", "-ra", "-p", "no:cacheprovider", "tests", "--junitxml=outputs/qa/rc1/pytest.xml")
    if args.stage in ("browser", "all"):
        run("browser", "scripts/check_agent3_dashboard.py", "--integrated")
    if args.stage in ("verify", "all"):
        # The verifier owns verification.json (its PASS report); keep the runner receipt separate.
        run("verification", "scripts/verify_rc1.py", receipt="verification_command.json")

if __name__ == "__main__":
    main()
