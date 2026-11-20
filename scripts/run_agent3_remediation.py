"""Run independent-audit corrections in separate candidate directories, preserving baseline."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jhim.remediation import run
from jhim.util import utf8_stdout

if __name__ == "__main__":
    utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True, help="Read-only auditor evidence directory")
    parser.add_argument("--high-perms", type=int, default=9999)
    parser.add_argument("--skip-spatial", action="store_true")
    parser.add_argument("--integrated", action="store_true", help="Consume canonical A1/A2 inputs; preserve audited comparisons")
    args = parser.parse_args()
    if args.high_perms < 999:
        parser.error("--high-perms must be >= 999")
    result = run(Path(__file__).resolve().parents[1], args.audit, args.high_perms, args.skip_spatial, args.integrated)
    print(f"Candidate valid grids: {result['n_valid']}; baseline preserved")
