# RC2 reproduction and verification

**Scope:** engineering remediation of the RC1 integration audit. This document
describes how to reproduce the **RC2 source candidate**, its frozen analytical
outputs, the clean-checkout test result, the portability checks and the
independent numerical verification. It does not approve a scientific model or
claim raw-data reproducibility without the separate frozen bundle.

## 1. Release identity and hash policy

| Item | Value |
|---|---|
| RC2 source build commit | `ac656e5b1b123d3bb5c5f618489682109bba2de9` |
| RC2 artifact commit | `267ebf78efc985926abd2ad64ec4d669138e1a6e` |
| RC1 frozen baseline | `3b8ed05be92c35bbb2b3a617688540ee856b11c8` |
| RC1 tree | `2b312d673faac64d51559cf9612caf61847ad226` |
| Source state at build | clean; no uncommitted source modifications |
| Receipt policy | `git-blob-sha256`: SHA-256 over `git cat-file blob <rev>:<path>` bytes |
| Output-manifest policy | exact-file SHA-256 with repository-relative POSIX paths; `data/**` and `outputs/**` are `-text` |

The RC1 receipt expected hashes were always canonical Git blobs. On a Windows
checkout with `core.autocrlf=true`, `handoff/RC1_HANDOFF.md`,
`handoff/RC1_VERIFICATION.md` and `docs/integration_manifest.json` appear to
mismatch only because the working-tree bytes are CRLF. RC2 makes that policy
explicit instead of silently rewriting RC1 evidence.

## 2. Environment actually used

- Windows x64, Python 3.12.10.
- Verified interpreter: `D:\jakarta-heat-integration\.venv\rc1\Scripts\python.exe`
  (the same pinned environment used by the independent RC1 re-audit).
- Exact package versions are captured in
  `outputs/qa/rc2/engineering_verification.json` and both rebuilt
  `run_manifest.json` files.
- `pip check` is part of the retained RC1 environment evidence; RC2 does not
  install or upgrade packages during the build.

A fresh user environment can be created with:

```powershell
python -m venv .venv/rc2
.venv/rc2/Scripts/python.exe -m pip install -r requirements.lock
```

The browser lane additionally needs the Playwright-pinned Chromium:

```powershell
.venv/rc2/Scripts/python.exe -m playwright install chromium
```

## 3. Clean-checkout source test (no raw data)

The WorldPop rasters are intentionally Git-ignored and are delivered in the
separate frozen-input bundle. A genuinely clean checkout must still run the
source suite and must not fail because `data/raw/worldpop/idn_pop_2024.tif` is
absent.

```powershell
git clone --no-hardlinks D:\jakarta-heat-rc2 D:\rc2-clean
cd D:\rc2-clean
$env:PYTHONDONTWRITEBYTECODE="1"
python -m pytest -q -ra -p no:cacheprovider tests `
  --basetemp=C:\Users\VICTUS\AppData\Local\Temp\rc2-clean-pytest
```

Expected: **236 tests + 7 subtests, 0 failed, 0 errors, 0 skipped**. The
source-manifest portability test checks the committed path contract and exercises
the hash verifier on a synthetic fixture; it does not read `data/raw`.

The RC2 result is recorded in `outputs/qa/rc2/pytest.xml` (and the clean-clone
run is reported separately in `outputs/qa/rc2/engineering_verification.json`).

## 4. Frozen inputs and source-manifest hashes

The raw bundle is not in Git. Restore it read-only or point the verifier at a
restored copy:

```powershell
python scripts/verify_source_manifests.py `
  --source-root D:\jakarta-heat-integration `
  --require-all `
  --json-out outputs\qa\rc2\source_manifest_check_frozen.json
```

Expected: 6/6 source raster hashes match (3 buffered corrected inputs + 3
original-mask inputs). Without a restored root, the same command reports the 6
paths as missing, not as a pass:

```powershell
python scripts/verify_source_manifests.py
```

The raw WorldPop/OSM/GraphML bundle itself is distributed as
`dist/agent2_frozen_inputs_v2.zip` with its `.sha256` sidecar. RC2 does not claim
that the raw bundle is reproducible from the network.

## 5. Rebuild the integrated analysis and replay

The analysis stage needs the read-only original audit evidence only for the
frozen comparison tables:

```powershell
python scripts/run_rc2.py --stage analysis `
  --audit-root D:\jakarta-heat-integration\audit
```

This performs, in order:

1. `scripts/run_agent3_remediation.py --integrated` (run 1);
2. `scripts/check_agent3_replay.py --capture` (snapshot run 1);
3. `scripts/run_agent3_remediation.py --integrated` (run 2);
4. `scripts/check_agent3_replay.py` (63-table semantic replay);
5. `scripts/run_agent3_pipeline.py` (standard M1–M4 pipeline);
6. `scripts/run_agent3_pipeline.py --p2-only` (Person 2 diagnostics).

The replay report is `outputs/qa/rc2/replay_verification.json`; the RC1 replay
evidence at `outputs/remediation/qa/replay_verification.json` is never
overwritten. Both runs must record the same implementation SHA, inputs, config
and actual runtime; the reported maximum numeric difference must be `0.0`.

## 6. Tests, dashboard and independent verification

```powershell
python scripts/run_rc2.py --stage tests
python scripts/run_rc2.py --stage browser
python scripts/run_rc2.py --stage verify `
  --audit-root D:\jakarta-heat-integration\audit `
  --source-root D:\jakarta-heat-integration
```

The browser stage uses Playwright-pinned Chromium and writes screenshots,
`browser_check.json` and the 254-row canonical M4 download under
`outputs/qa/rc2/dashboard/`. Edge/Firefox/Safari are not claimed.

`scripts/verify_rc2.py` independently recomputes M1–M4 from `merged_grid.csv`
(without the `jhim` scoring functions), rebuilds the Queen graph with libpysal,
recomputes Moran/LISA with esda, checks the output manifests, confirms the
baseline model files are byte-identical to RC1, compares the dashboard loader to
the canonical priority table, and writes:

- `outputs/qa/rc2/engineering_verification.json`
- `docs/RC2_BUILD_RECORD.json`
- `docs/integration_manifest.json`

Expected counts:

| Quantity | Expected |
|---|---:|
| Master grid IDs | 2,765 |
| Common comparison grids | 2,536 |
| Spatial observations after one island | 2,535 |
| Queen directed edges | 18,368 |
| Moran M4 (Queen) | 0.593024953816681 |
| M1/M2 eligibility | 2,764 / 2,764 |
| M3/M4 eligibility | 2,758 / 2,536 |
| Standard output manifest | 69/69 |
| Remediation output manifest | 80/80 |

## 7. Receipt and portability checks

```powershell
python scripts/verify_receipt_hashes.py `
  --receipt handoff/RC1_CANDIDATE_RECEIPT.json `
  --rev 3b8ed05be92c35bbb2b3a617688540ee856b11c8 `
  --json-out outputs\qa\rc2\rc1_receipt_hash_check.json

python scripts/verify_portability.py `
  --source-root D:\jakarta-heat-integration

python scripts/verify_receipt_hashes.py `
  --receipt handoff/RC2_CANDIDATE_RECEIPT.json `
  --rev HEAD `
  --json-out outputs\qa\rc2\rc2_receipt_hash_check.json
```

Expected: RC1 receipt **9/9**, RC2 receipt **9/9**, standard output manifest
**69/69**, remediation output manifest **80/80**, current manifests free of
`D:\`/`C:\`/`/home/`/`/Users/` paths, and 6/6 source-manifest hashes when a
frozen root is supplied.

`docs/integration_manifest.json` is the live RC2 manifest. Its RC1 version is
preserved by the archival receipt at commit `3b8ed05`; RC2 does not rewrite the
RC1 handoff or verification documents.

## 8. What this reproduction does not establish

- No original GEE scene/task/AOI lineage; “2024” remains a declared recipe period.
- No verified public park entrance, legal connector or 2024 access claim.
- No health, causal, predictive-accuracy or policy-superiority claim.
- No scientific sign-off of model weights, thresholds, aggregation, LISA
  convention or novelty. Those remain with the research-methodology workstream
  and independent coordinator.
- No Linux/macOS or non-Chromium browser execution pass. The hash policy is
  portable by construction; the executed environment is Windows x64.
