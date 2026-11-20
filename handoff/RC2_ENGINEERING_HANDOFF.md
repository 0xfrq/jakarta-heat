# RC2 engineering handoff

**Status: PASS for engineering portability and numerical reproduction; scientific HOLD.**
**Scope:** close the engineering portability and provenance findings in the
independent RC1 re-audit without redesigning the scientific model.
**Scientific release:** **HOLD**. RC2 does not sign model weights, thresholds,
constructs, access claims, novelty or policy conclusions.

## 1. Release identity

| Item | Value |
|---|---|
| Branch | `integration/rc2` |
| RC2 source build commit | `ba033d98a04e1d76d964bea6b8ee1b154ab02e03` |
| Source state at build | `clean`; dirty source paths: none |
| RC2 artifact commit | `8f740675e25b3372ad8d2aba7ad2ece6bb45852a` |
| RC1 frozen baseline | `3b8ed05be92c35bbb2b3a617688540ee856b11c8` (tree `2b312d673faac64d51559cf9612caf61847ad226`) |
| Implementation SHA-256 | `59ff6061fd1aca3649c0eb331dcda8c7b0d17a39c54c222624b0789d2e19ba49` |
| Build commands | `python.exe scripts/run_agent3_remediation.py --integrated --audit <external>/audit`, then `python.exe scripts/run_agent3_pipeline.py` |
| Replay | PASS: 63 tables/metadata compared; maximum absolute numeric difference `0.0`; both runs have the same implementation SHA |

The RC2 build is not described as clean merely because generated outputs changed.
`jhim.util.git_source_state` separates generated analytical artefacts
(`data/processed/modeling*`, `data/processed/integrated_comparisons`,
`outputs/tables|figures|gis|remediation|qa/agent3|qa/rc1|qa/rc2`) from
uncommitted source, configuration or documentation files. Both rebuilt run
manifests record the same clean `source_revision`; the artifact commit is later
because it stores the regenerated outputs. Full detail is in
`docs/RC2_BUILD_RECORD.json`.

## 2. RC1 findings closed in RC2 engineering

### C1 — clean-checkout test failure

The failing test was
`tests/test_agent2_remediation.py::test_source_manifests_are_portable_relative_paths`.
It read `data/raw/worldpop/idn_pop_2024.tif`, which is intentionally Git-ignored.
RC2 now:

- asserts the committed manifests contain three unique features, repository-relative
  POSIX paths, no drive letter/backslash/parent escape, and 64-hex SHA-256 values;
- exercises the same hash verifier on a self-contained synthetic fixture,
  including mutation detection;
- provides `scripts/verify_source_manifests.py --source-root ... --require-all`
  for the real frozen raster hashes.

A genuine clone of `integration/rc2` (no `data/raw`, no `dist`) ran the full suite:
**236 tests + 7 subtests, 0 failed, 0 errors, 0 skipped**. The real raw hash check
is explicitly optional and requires the separate bundle; RC2 does not claim the
raw data are in Git.

### C2 — receipt and hash consistency

RC1's receipt expected hashes are canonical Git blobs. On Windows with
`core.autocrlf=true`, three checkout files are CRLF and therefore hash differently
from their LF blobs. RC2 documents and uses one policy:

> **`git-blob-sha256`** — SHA-256 over `git cat-file blob <rev>:<path>` bytes.
> The checkout representation is irrelevant.

`scripts/verify_receipt_hashes.py` verifies the archival RC1 receipt at
`3b8ed05` and the RC2 receipt at the RC2 candidate. The RC1 receipt is **9/9**
under this policy; RC1 evidence was not rewritten. The three disk-byte
mismatches are retained in `outputs/qa/rc2/portability_verification.json` as
documented before/after evidence.

### C3 — portable manifest paths

`jhim.provenance.inputs_identity` and `output_identity` now emit
repository-relative POSIX paths. Build commands are also sanitized
(`--audit <external>/audit`) so run manifests do not embed a machine path. Both
`output_sha256_manifest.csv` files and the live
`docs/integration_manifest.json` resolve from any checkout. The standard
manifest has **69/69** entries and the remediation manifest **80/80**; no entry
uses `D:\jakarta-heat-integration`.

### C4 — documentation drift

`docs/spatial_inference_spec.md` and `docs/external_validation_scope.md` now say
**2,536 common comparison grids** and **2,535 spatial observations** after the
single Queen island `JKT_R013_C019`. The old 2,526 figure is retained only where
it genuinely describes the original-mask null-exclusion candidate. The remote
sensing manifest labels `cdda424...` and its uncommitted state as historical
Agent 1 provenance and points current release binding to
`docs/RC2_BUILD_RECORD.json`.

### C5 — release identity

RC1 involved three commits and a `f1e69a3-dirty` build. RC2 records the actual
source revision, clean source state, dirty paths, build command, artifact
revision and artifact tree separately. No claim is made that the RC1 build was
clean. RC2's source snapshot is committed before the frozen outputs are
regenerated.

## 3. Verification results

| Check | RC2 result |
|---|---|
| Clean-checkout source suite | 236 tests + 7 subtests; 0 failed, 0 errors, 0 skipped (genuine clean clone) |
| Replay | PASS: 63 tables/metadata; maximum absolute numeric difference `0.0`; same implementation SHA |
| Master grid IDs | 2,765 |
| Common comparison grids | 2,536 |
| Spatial observations | 2,535 |
| Queen directed edges | 18,368 |
| Moran M4 (Queen) | 0.593024953816681 |
| M1/M2/M3/M4 eligibility | M1 2,764; M2 2,764; M3 2,758; M4 2,536 |
| Standard output manifest | 69/69 relative; 0 absolute, 0 missing, 0 mismatched |
| Remediation output manifest | 80/80 relative; 0 absolute, 0 missing, 0 mismatched |
| RC1 receipt (canonical blobs) | 9/9 (archival receipt verified at `3b8ed05`) |
| RC2 receipt (canonical blobs) | 9/9 expected under the same policy; separate check `outputs/qa/rc2/rc2_receipt_hash_check.json` |
| Dashboard freshness | PASS: 2,765 feature rows; scores/ranks match; official outputs current. Browser: 8/8 routes, 0 page errors, 254-row M4 download exact, 5/6 interactions visible |
| Baseline model definitions | Byte-identical to RC1; `PROVISIONAL_UNSIGNED`; no weights/threshold/construct change |

Detailed machine-readable evidence:

- `outputs/qa/rc2/engineering_verification.json`
- `outputs/qa/rc2/portability_verification.json`
- `outputs/qa/rc2/rc1_receipt_hash_check.json`
- `outputs/qa/rc2/rc2_receipt_hash_check.json`
- `outputs/qa/rc2/replay_verification.json`
- `outputs/qa/rc2/clean_checkout_report.json`
- `outputs/qa/rc2/pytest_clean_checkout.xml`

## 4. Before/after differences

| Area | RC1 | RC2 |
|---|---|---|
| Clean checkout | 235 pass, 1 fail (`data/raw` absent) | 236 tests + 7 subtests pass, 0 fail/error/skip |
| Receipt policy | Mixed: 6/9 disk, 9/9 canonical blobs unexplained | One documented `git-blob-sha256` policy; RC1 9/9 and RC2 9/9 |
| Output manifest paths | 69/69 absolute `D:\jakarta-heat-integration` | 69/69 relative; remediation 80/80 relative |
| Spatial denominator docs | 2,526 / 2,526; island statement wrong | 2,536 common / 2,535 tested after island |
| Remote-sensing provenance | `git_head cdda424...`, “uncommitted ... not an integrated release” | Historical labels plus current RC2 binding |
| Build identity | `f1e69a3-dirty`; three commits conflated | Clean source commit `ba033d9`, artifact commit `8f74067` |
| Scientific model | M1–M4 provisional | Unchanged; byte-identical definitions, still `PROVISIONAL_UNSIGNED` |

The standard manifest has 16 RC1-baseline hash changes, all in
`merged_meta.json`/`priority_meta.json`, 14 SVG files and the standard GPKG.
Inspection shows the SVG changes are Matplotlib `<dc:date>` and generated clip
IDs; PNG figures and all numerical tables are byte-identical. The remediation
manifest has three baseline changes: two meta JSON files and the GPKG container.
The two-run replay compares 63 tables/metadata at tolerance `1e-12` with maximum
difference `0.0`, and reports GPKG container bytes separately from geometry and
table equality. RC2 does not treat a container-byte change as a numerical change.

## 5. Scientific dependencies that remain

RC2 does **not** close any of the following:

- RS-01 acquisition lineage (scene/task/AOI), or an approved “declared 2024
  recipe period” claim restriction.
- RS-02 thermal support threshold (0.50 remains provisional).
- NV-01 novelty/literature/contribution.
- M4 construct, age-count collinearity, and the mechanical park-term exclusion
  of near-park cells from the top 254.
- Selection inference beyond the 2,536 common set; 229 excluded grids and 13
  route-missing candidates remain disclosure items.
- LISA convention choice; no `p=0`, causal or “all priorities robust” claim.
- Park access/connector legality; baseline routes remain modeled and unvalidated.
- Hybrid versus fractional population aggregation.
- Dynamic World categorical deferral.
- Signed scientific decisions D1–D13 and QA-01.

See `handoff/RC2_ENGINEERING_OPEN_ISSUES.md` for the itemised list.

## 6. Integration readiness

RC2 engineering is ready for the research-methodology branch to be integrated,
provided that branch does **not** change model definitions, weights, thresholds
or eligibility. If it does, regenerate the RC2 build and verification rather
than relabelling this evidence. Scientific sign-off (RS-01, NV-01, M4 construct,
D1–D13, QA-01) remains **HOLD**.

## 7. Review locations

| Item | Location |
|---|---|
| RC2 reproduction commands | `docs/RC2_REPRODUCE.md` |
| RC2 manifest | `docs/integration_manifest.json` |
| RC2 build record | `docs/RC2_BUILD_RECORD.json` |
| Independent numerical verification | `outputs/qa/rc2/engineering_verification.json` |
| Portability and receipt verification | `outputs/qa/rc2/portability_verification.json` |
| Clean-checkout test report | `outputs/qa/rc2/clean_checkout_report.json`, `outputs/qa/rc2/pytest_clean_checkout.xml` |
| Two-run replay | `outputs/qa/rc2/replay_verification.json` |
| Dashboard evidence | `outputs/qa/rc2/dashboard/`, `outputs/qa/rc2/browser_summary.json` |
| RC1 baseline receipt | `handoff/RC1_CANDIDATE_RECEIPT.json` |
| RC1 immutable evidence | `handoff/RC1_HANDOFF.md`, `handoff/RC1_VERIFICATION.md` (unmodified) |
