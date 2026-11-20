# RC2 engineering open issues and scientific dependencies

**Status:** RC2 engineering remediation is being closed against the RC1 independent
re-audit. This file separates **engineering issues in RC2 scope** from
**scientific/methodological issues that RC2 must not silently fix**. It does not
approve any scientific decision and does not close QA-01.

## 1. Engineering issues addressed in RC2

| ID | RC1 finding | RC2 disposition | Evidence |
|---|---|---|---|
| C1 | `test_source_manifests_are_portable_relative_paths` failed in a clean checkout because the Git-ignored WorldPop raster was absent | Split the test contract: committed manifests are checked for repository-relative POSIX paths and hash format; the verifier is exercised on a synthetic fixture; the real hash check is an explicit frozen-input command (`scripts/verify_source_manifests.py --source-root ... --require-all`) | `tests/test_agent2_remediation.py`, `outputs/qa/rc2/engineering_verification.json` |
| C2 | 3/9 RC1 receipt hashes failed on a Windows checkout | Adopted one explicit policy: `git-blob-sha256` over `git cat-file blob <rev>:<path>`, with exact-file SHA-256 for output manifests whose paths are `-text` | `scripts/verify_receipt_hashes.py`, `outputs/qa/rc2/portability_verification.json`, `handoff/RC1_CANDIDATE_RECEIPT.json` |
| C3 | 69 output entries used `D:\jakarta-heat-integration\...` | Output manifests and integration/run manifests now use repository-relative POSIX paths and resolve from any checkout | `data/processed/modeling/output_sha256_manifest.csv` (69/69), `data/processed/modeling_remediation/output_sha256_manifest.csv` (80/80) |
| C4 | `spatial_inference_spec.md` and `external_validation_scope.md` said 2,526; remote-sensing manifest presented `cdda424...` as current | Corrected to 2,536 common comparison / 2,535 spatial after island exclusion; historical Agent 1 identity is explicitly labelled archival and bound to the RC2 build record | `docs/spatial_inference_spec.md`, `docs/external_validation_scope.md`, `docs/remote_sensing_export_manifest.json` |
| C5 | RC1 build ran at `f1e69a3-dirty`; three commits were conflated | RC2 records the exact clean source revision, source state, dirty paths (none), artifact revision and build command in `docs/RC2_BUILD_RECORD.json`; generated outputs are excluded from the source-dirty test | `docs/RC2_BUILD_RECORD.json`, `docs/integration_manifest.json`, both `run_manifest.json` files |

## 2. Scientific issues that remain deliberately open

These are **not** RC2 engineering defects and must not be closed by a software
pass. They belong to the research-methodology workstream.

| Issue | Why it remains open | RC2 treatment |
|---|---|---|
| RS-01 acquisition lineage | Original GEE scene/task/AOI records are unavailable; the scene manifest is header-only and “2024” is a declared recipe period | Values and rasters unchanged; no acquisition-origin claim; remote-sensing manifest labels the old `cdda424` state as historical |
| RS-02 thermal support threshold | 0.50 is provisional and unsigned; `JKT_R037_C062` has 27.759% support | Values and flags unchanged; no new threshold decision |
| NV-01 novelty/contribution | Combination-only claim failed; no signed contribution or updated literature matrix | Not addressed in RC2 engineering |
| M4 construct | `vuln` is nearly collinear with total population; the additive park term mechanically excludes near-park cells from the top 254 | Baseline model definitions are byte-identical to RC1 and remain `PROVISIONAL_UNSIGNED`; no redesign or relabel was performed here |
| Selection inference | Common set is 2,536 of 2,765; 229 excluded, 13 route-missing may enter the top 254 | Counts and selection outputs preserved; RC2 does not claim Jakarta-wide inference |
| Local inference convention | LISA labels are convention-sensitive (directed/999/BH 663; two-sided 496; 9,999 variants) | Saved conventions and sensitivity table preserved; no p=0 or causal claim |
| Park access / connector legality | 0 verified public entrances; baseline routes are modeled and unvalidated; conservative route count is 407 | No access or legal-route claim added |
| Population aggregation | Hybrid primary is unsigned; fractional is a sensitivity; 16 top-cell swaps | Primary outputs unchanged; no new aggregation decision |
| Dynamic World categorical deferral | Categorical labels remain absent; probability is not a fraction | No categorical-area claim |
| Scientific sign-off | D1–D13 decisions remain unsigned; QA-01 remains with independent review | RC2 reports engineering readiness only |

## 3. Residual engineering limitations

1. **Frozen raw data are not in Git.** `data/raw/` is intentionally ignored. A
   clean source checkout can run the suite and verify manifest paths, but exact
   source-raster hashes require the separate frozen bundle or a read-only
   restored root. RC2 does not claim raw-data reproducibility without it.
2. **Browser scope is Chromium only.** The RC2 rerun passed 8/8 routes, 0 page
   errors and the 254-row M4 download, but one harness locator (custom-weights
   toggle) did not activate in the last run; 5/6 interactions were visible.
   Dashboard freshness is independently verified by `scripts/verify_rc2.py`.
   Edge/Firefox/Safari are not claimed.
3. **GPKG container bytes are serializer-dependent.** RC2 compares tables,
   IDs, scores, ranks and geometry; a GPKG byte difference is reported as a
   container difference, not silently treated as numerical equality.
4. **Windows x64 is the verified platform.** The hash policy is portable by
   construction (canonical Git blobs), but RC2 does not claim a Linux/macOS
   execution pass.
5. **The original RC1 directory is read-only evidence.** RC2 must not rewrite
   RC1 handoff, verification or audit files. `docs/integration_manifest.json` is
   the live manifest and is intentionally superseded; its RC1 version remains
   bound by the archival RC1 receipt at `3b8ed05`.

## 4. What must be true before the research-methodology branch is integrated

- RC2 engineering verification reports PASS for counts, model arithmetic,
  spatial arithmetic, output hashes, source-manifest portability and build
  identity.
- The clean-checkout test run reports zero failures and zero unexpected skips.
- The research-methodology branch states whether it changes model definitions,
  weights, thresholds, eligibility or claim scope; if it does, RC2 engineering
  evidence must be rebuilt rather than relabelled.
- Scientific decisions D1–D13 and QA-01 remain the coordinator/independent
  reviewer’s responsibility.
