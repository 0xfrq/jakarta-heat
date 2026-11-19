"""Restore frozen inputs, explicitly reconciling Git newline conversion with archived bytes.

Only newline-equivalent tracked copies may be changed, after preserving originals.
Any other mismatch fails; original audit files are outside the allowed path inventory.
"""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
bundle = ROOT / "dist/agent2_frozen_inputs_v2.zip"
def digest(data):
    return hashlib.sha256(data).hexdigest()
expected_bundle = bundle.with_suffix(".sha256").read_text().split()[0]
assert digest(bundle.read_bytes()) == expected_bundle, "Bundle SHA256 mismatch"
manifest = json.loads((ROOT / "docs/agent2_frozen_inputs.json").read_text())
repairs = []
with zipfile.ZipFile(bundle) as archive:
    for item in manifest["inputs"]:
        target = (ROOT / item["path"]).resolve()
        assert target.is_relative_to(ROOT) and not target.is_relative_to(ROOT / "audit")
        data = archive.read(item["path"])
        assert digest(data) == item["sha256"]
        if target.exists():
            before = target.read_bytes()
            if digest(before) == item["sha256"]:
                continue
            if before.replace(b"\r\n", b"\n") != data.replace(b"\r\n", b"\n"):
                raise ValueError(f"Non-newline input mismatch: {target}")
            backup = ROOT / "dist/checkout_originals" / item["path"]
            backup.parent.mkdir(parents=True, exist_ok=True)
            if not backup.exists():
                backup.write_bytes(before)
            repairs.append({"path": item["path"], "checkout_sha256": digest(before),
                            "frozen_sha256": digest(data), "reason": "newline-only Git checkout conversion"})
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
if repairs:
    (ROOT / "outputs/qa/rc1/frozen_checkout_repairs.json").write_text(json.dumps(repairs, indent=2), encoding="utf-8")
print(f"Verified bundle and restored {len(manifest['inputs'])} inputs; {len(repairs)} newline-only repairs")
