# RC1 handoff for Independent Re-audit

**Status: READY FOR INDEPENDENT RE-AUDIT (engineering evidence complete).**
The consolidated empirical rebuild, two-run semantic replay, full test suite,
pinned-browser checks, independent arithmetic/data/GIS/provenance verifier and
release-evidence gate all pass on source build
`f1e69a370f743985977e3d90c59179c76eea35d9`.

Final-paper release remains **HOLD**. Software readiness does not approve the
scientific choices, does not close QA-01, and does not amend the original audit.
The exact final artifact commit is reported in the delivery message and in the
separate `dist/rc1_candidate_receipt.json`; it is later than the source build
commit because rebuilt outputs and evidence are committed after the build.

RC1 combines Agent 1 `4f6c679`, Agent 2 `e713342` and Agent 3 `7ec9b2e` on
`integration/rc1`, from main baseline `f9b5c02`. Both requested merges are complete.
The only merge conflict was README content; both sections were retained.
The original main branch and three agent worktrees were not modified. Nothing
was pushed or merged into main. Full SHAs and conflict handling are in
[`RC1_SOURCE_AND_CONFLICTS.md`](../docs/RC1_SOURCE_AND_CONFLICTS.md).

The integration corrects an interface defect that a merge alone could not fix:
Agent 3's original remediation runner forced an audit-derived RS/support copy.
`--integrated` now uses the revised A1 export and corrected A2 demographic counts,
support and aggregation alternatives. All five A2 route scenarios are replayed
by exact grid ID. The primary measured-route proxy remains the provisional
baseline; conservative and positive-tag assumptions remain labeled alternatives.
Both `raw_*` and `*_raw` columns survive ingestion. Demo mode cannot consume
real demographic overrides.

## Verified engineering evidence

| Check | Final observed result |
|---|---|
| Actual-data upstream rebuild | Agent 1 GeoTIFFs aggregated; 49 RS QA checks with zero critical failures; all 2,765 master IDs retained |
| Original demographic masks | 19 age-no-support cells / 6 total-no-support cells reproduced |
| Buffered corrected demographics | 6 unsupported total/child/elderly cells remain; 13 originally unsupported age cells recovered; `agent2-DM-01-v1-buffered-age` |
| Expanded model candidate | 2,536 common eligible grids; 254-grid top-10% budget; 226 unknown baseline routes / 407 under conservative restrictions |
| Two-run replay | PASS: 63 tables/metadata; maximum numeric difference `0.0`; GIS attributes and geometries equal; figures byte-identical |
| Standard full pipeline | PASS: merge, priority, comparison, spatial (999 permutations), sensitivity (9,999 high-permutation), export; 27 figure/GIS exports |
| Full test suite | PASS: 236 tests plus 7 subtests; zero failures, errors or skips; canonical A1 contract test executed and passed |
| Independent verifier | PASS: canonical A1/A2 adoption, equations/ranks/top sets, GIS identity, Shapley/BH/BY, manual Moran M4 `0.593024953816681`, dashboard/model equality, fresh manifests, unchanged audits and refs |
| Browser | PASS on Playwright-pinned Chromium `159.0.8154.6`: 8/8 routes, continuous navigation, 18 screenshots, 6 interactions, 254-row canonical M4 download |
| Post-build freshness | PASS: fresh outputs visible, missing-RS explicit pending, demo explicitly synthetic |
| Release-evidence gate | PASS: `outputs/qa/rc1/release_evidence_verification.json` |

The final suite's fixture identity equals both final pipeline manifests at
implementation SHA `6b2eae9dc37b14d92bd6accafda602da1e42af643ba8a72b6431d60e985b233e`.
There are zero implementation-file differences between the tested source and the
manifested source. The prior suite at `6759fe9` is retained as
`outputs/qa/rc1/full_suite_source_identity_pre_source_fix.json`.

A last defect was found and fixed before this handoff: the runner's `verify`
stage reused `outputs/qa/rc1/verification.json` for its command receipt,
overwriting the verifier's PASS report. The receipt is now
`outputs/qa/rc1/verification_command.json`; `verification.json` is the report.
Because the fix changed implementation identity, the analytical pipeline,
replay, full suite, browser and post-build checks were all repeated on the final
source. No hash was refreshed without rerunning the corresponding evidence.

## Review locations

| Review item | Location |
|---|---|
| Current canonical paths and input hashes | `docs/integration_manifest.json` |
| Reproduction commands and contract | `docs/RC1_REPRODUCE.md` |
| Verification, failure disposition and limits | `handoff/RC1_VERIFICATION.md` |
| Issue-by-issue implementer disposition | `handoff/RC1_ISSUE_LEDGER.csv` |
| Independent arithmetic/data/GIS report | `outputs/qa/rc1/verification.json` |
| Release-evidence gate report | `outputs/qa/rc1/release_evidence_verification.json` |
| Per-command logs, receipts and test XML | `outputs/qa/rc1/` |
| Standard features / priorities | `data/processed/modeling/` |
| Standard tables / maps / GIS | `outputs/tables`, `outputs/figures`, `outputs/gis` |
| Expanded attribution / selection / scenarios | `outputs/remediation/`, `data/processed/modeling_remediation/` |
| Semantic replay | `outputs/remediation/qa/replay_verification.json` |
| Browser screenshots / canonical download | `outputs/qa/rc1/dashboard/` |
| Original audit identity | `outputs/qa/rc1/original_audit_hashes.json` |

Use [`RC1_REPRODUCE.md`](../docs/RC1_REPRODUCE.md) for environment, frozen-input
restore and full commands. Required artifacts include the Git candidate, the
hash-verified `dist/agent2_frozen_inputs_v2.zip` and checksum, and the original
read-only audit package. The Agent 1 GeoTIFF exports are tracked in Git; their
hashes are checked before aggregation. The raw WorldPop/OSM/GraphML closure is
restored from the separate bundle.

The original `audit/` files remain unchanged and are supplied separately. New
verification evidence does not amend their issue statuses or acceptance rows.
Historical workstream ledgers retain their earlier scope; the RC1 handoff and
manifest describe the consolidated candidate. Frozen QA Python code is archived
as `.py.txt`, and its old integration stage refuses execution.

## Scientific decisions still reserved

Independent review must still assess acquisition lineage and seasonal sampling,
physical park entrances and connector evidence, mixed-period scope approval,
primary allocation/count/share/weight/support policy, inference family and
novelty/claim scope. No software pass signs those choices. The 16-scenario
factorial covers construct/cap/normalization/aggregation; route-policy variants
are a separate family, so no all-family joint robustness claim is made.

Specific retained limits: the GEE scene/task/AOI lineage is incomplete and the
scene manifest is header-only (unavailable records, not zero scenes); seasonal
representativeness is unproven; optional categorical DW labels remain absent and
fractions stay null; zero physical/public park entrances are verified; OSM
parks/network 2026 are paired with 2024 thermal/demographic data; the historical
pilot HTTP 406 establishes no temporal stability; the 226/407 route counts are
assumption-bound proxies. No health, causal, predictive-accuracy or
policy-superiority claim is validated. QA-01 and all acceptance decisions remain
with Independent Re-audit.
