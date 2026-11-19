"""Record immutable audit/source identity before RC1 execution (standard library only)."""
import hashlib
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
out = root / "outputs/qa/rc1"
out.mkdir(parents=True, exist_ok=True)
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
target = out / "original_audit_hashes.json"
if not target.exists():
    audits = {str(d): {p.relative_to(d).as_posix(): digest(p) for p in d.rglob("*") if p.is_file()}
              for d in [Path("D:/jakarta-heat/audit"), root / "audit"]}
    target.write_text(json.dumps(audits, indent=2), encoding="utf-8")
refs = {n: subprocess.check_output(["git", "rev-parse", n], text=True).strip()
        for n in ["main", "agent/person1", "agent/person2", "agent/person3"]}
(out / "source_refs.json").write_text(json.dumps(refs, indent=2), encoding="utf-8")
print(refs)
