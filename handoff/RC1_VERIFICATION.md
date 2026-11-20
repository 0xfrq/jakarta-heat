# RC1 verification record

**Status: PASS for engineering readiness. No scientific approval implied.**
This record covers the consolidated workspace at source build
`f1e69a370f743985977e3d90c59179c76eea35d9`, implementation SHA
`6b2eae9dc37b14d92bd6accafda602da1e42af643ba8a72b6431d60e985b233e`.
Final-paper release remains **HOLD** pending independent scientific review and
coordinator decisions. The final artifact commit is reported separately in the
delivery message and `dist/rc1_candidate_receipt.json`.

| Check | Final observed result / evidence |
|---|---|
| Source tips and merges | Supplied tips verified; A1/A3 merged into `integration/rc1`; README sections retained; main and agent tips unchanged |
| Fresh environment | Python 3.12.10 Windows x64 venv; all 66 lock pins match; `pip check` passes (`outputs/qa/rc1/environment.json`) |
| Frozen input closure | 55 hashes verified; bundle SHA256 `3fc027ed47b8fb122f8d5ed3fdc3bec7f306d6a358e99ee0c2e42bb00c011f3a` |
| A1 rebuild | Actual GeoTIFFs aggregated; 49 validator checks, zero critical failures; sampled LST/NDVI/DW probability intersections pass |
| Original demographics | 19 age-no-support / 6 total-no-support cells reproduced from original masks |
| Corrected demographics | 6 unsupported total/child/elderly cells reproduced; 13 age cells recovered from buffered surfaces; support version `agent2-DM-01-v1-buffered-age` |
| Parks | Shortest-path comparison passes; all 20 influential initial samples remain explicitly reviewed/unresolved; zero verified entrances |
| Restrictions/connectors | 24,370 directed edges removed by the declared conservative screen; 167 origin / 78 park connector conflicts; 226 baseline / 407 conservative unknown routes |
| Consolidated expanded models | Two complete real-data runs; 2,536 common eligible grids and 254 top-10% grids |
| Two-run replay | **PASS**: 63 tables/metadata; max numeric difference `0.0`; GIS attributes/geometry equal; figures byte-identical; same implementation SHA for both runs |
| Standard full pipeline and population diagnostics | **PASS**: merge/priority/comparison/spatial/sensitivity/export; 27 figure/GIS exports; `--p2-only` diagnostics pass |
| All workstream tests | **PASS**: 236 tests plus seven subtests; zero failures/errors/skips; one expected missing-CRS warning |
| All eight browser routes / interactions / downloads | **PASS** on Playwright-pinned Chromium `159.0.8154.6`: continuous navigation; 16 route screenshots plus two interaction captures; six interactions; 254-row M4 download matches canonical IDs/scores/ranks/scope |
| Post-build freshness | **PASS**: fresh outputs visible, missing-RS state explicit, demo marked synthetic (`outputs/qa/rc1/dashboard/postbuild_verification.json`) |
| Independent equations / GIS / dashboard / manifest checks | **PASS**: `outputs/qa/rc1/verification.json`; 2,765 master, 2,536 common, manual Moran M4 `0.593024953816681` |
| Original audits and source refs preserved | **PASS**: original audit hashes and source refs unchanged; verifier checked both |
| Release-evidence gate | **PASS**: `outputs/qa/rc1/release_evidence_verification.json` |

Commands and complete output are logged with exit receipts under
`outputs/qa/rc1/`. The consolidated runner stops at a nonzero exit code. The
verifier owns `verification.json`; the runner's command receipt is
`verification_command.json`. Source and output identities are stored independently
of Git's dirty marker: model execution writes generated artifacts before its
manifest, so a recorded `-dirty` suffix alone does not establish dirty scientific
code. The source build commit and final artifact commit are distinct identities.

## Final test provenance

The suite passed in one consolidated invocation on source commit `f1e69a3`:
A1 40 tests; A2 69 tests plus seven subtests; A3 125 tests (including 30 dashboard
AppTests); RC1 boundary checks two tests. The XML reports 243 outcomes including
subtests, with zero failures, errors or skips. The former canonical-A1 skip is
revisited by `test_real_agent1_remote_sensing_contract`: exactly one testcase is
present and it passed, with no skipped/failure/error node. The only warning is
deliberate creation of a CRS-free fixture in `test_grid_without_crs_rejected`.

The suite's fixture manifest captured the actual implementation file hashes,
including the generated scenario registry. Those hashes are retained in
`outputs/qa/rc1/full_suite_source_identity.json`. Its implementation SHA equals
both final pipeline manifests, so `changed_since_full_suite` is empty. The
earlier suite at `6759fe9` is retained as
`full_suite_source_identity_pre_source_fix.json` and `test_summary_pre_source_fix.json`;
it is historical evidence only and is not used by the final gate.

## Report/receipt collision fixed before handoff

The verifier writes its independent PASS report to
`outputs/qa/rc1/verification.json`. The generic runner receipt previously used
the same filename for the `verify` stage, so the report was overwritten by a
one-line command receipt. The defect was reproduced in the retained
pre-fix receipt state and fixed in the source build commit by giving the stage a
distinct `verification_command.json` receipt.

Because `scripts/run_rc1.py` is part of implementation identity, the fix changed
the source hash. The complete analytical pipeline and replay were therefore
rerun, followed by the full suite, browser run, post-build check and release
gate. The final `verification.json` contains `"result": "PASS"`, not a command
receipt, and its mtime/content match the verifier log. The runner no longer
overwrites it.

## Investigated interruptions and mismatches

1. Git initially required access to its worktree metadata outside the workspace.
   The Agent 1 merge completed after permission; the interrupted Agent 3 merge
   was checked before continuing. No partial merge was assumed complete.
2. Frozen restore rejected three park HTML checkouts. Comparison proved the
   differences were only CRLF/LF conversion. Original checkout bytes were kept
   under `dist/checkout_originals`; both hashes are in
   `outputs/qa/rc1/frozen_checkout_repairs.json`. The bundle's exact bytes were
   restored, then all 55 inputs passed. Non-newline mismatches still fail.
   `.gitattributes` preserves hashed artifact/implementation bytes on checkout.
3. Preliminary fixture tests were aborted while graph screening caused memory
   pressure on the 8 GB host. This is explicitly **not a passing test run**.
   `initial_interface_tests_status.json` records the interruption. All final
   tests ran sequentially after the empirical rebuild.
4. The previous Agent 3 canonical-RS skip is revisited by the final suite's
   `test_real_agent1_remote_sensing_contract`. The XML confirms exactly one
   executed passing case, with no skipped/failure/error node. No tests remain
   skipped.
5. The initial replay helper emitted a historical sentence excluding integrated
   scope even when the manifest source was integrated. The helper now derives
   scope from that actual source. The earlier numerical PASS is retained as
   `replay_before_scope_fix.json`; authoritative final capture/replay was
   repeated after the fix so implementation hashes match.
6. System Edge 157 crashed during route/capture checks, including continuous
   navigation at the spatial view. A documented SwiftShader probe timed out
   at startup (60 seconds, then 240 seconds); server logs showed no application
   exception. Those failures are retained under `browser_*crash*`,
   `browser_software_*` and `dashboard_initial_crash/`. The final harness uses
   Playwright's own pinned Chromium 159 build, installed with the recorded
   command. It passed continuous navigation through all eight pages, isolated
   desktop/narrow captures, actual downloads and all six interactions with no
   page errors. The exact Edge/driver failure mechanism is unproven; the verified
   browser scope is pinned Chromium, and no Edge compatibility pass is claimed.
   The experimental flags followed [Chromium's SwiftShader documentation](https://chromium.googlesource.com/chromium/src/+/refs/heads/main/docs/gpu/swiftshader.md);
   they are absent from the successful final browser command.
7. The post-build checker's first attempt wrongly expected dataframe canvas text
   to appear in DOM `inner_text`. The assertion was corrected to visible caption
   plus canonical manifest path. The failed attempt is retained as
   `postbuild_canvas_dom_assertion.*`; the passing result is in
   `dashboard/postbuild_verification.json`.

## Artifact byte storage and post-commit binding

The final candidate is checked against the Git tree, not only the working
directory. All hash-bearing implementation, input, output, frozen-input and A1
export files are stored with their exact bytes (`-text` attributes), so a fresh
checkout reproduces the manifest SHA256 values. An intermediate artifact commit
retained legacy LF blobs for some unchanged CRLF source/input files; the final
commit re-stored those exact bytes without changing file content, manifests or
analytical results. Post-commit checks compare every manifest hash with
`git cat-file blob HEAD:<path>` and the committed tree is required to be clean.
The source build commit remains `f1e69a3`; the final artifact commit is the later
commit reported in the delivery message and `dist/rc1_candidate_receipt.json`.

## Limits retained for independent review

The offline lane reproduces local frozen exports, source masks, graph and
archived evidence through analytical outputs. It does not recover original GEE
task/scene/AOI lineage or establish seasonal representativeness. The scene
manifest remains header-only, meaning unavailable records, not zero scenes.
Optional categorical DW labels remain absent/null; probability values are not
categorical fractions. Formal supplementary deferral still needs a decision.

OSM parks/network refer to November 2026; thermal/demographic sources refer to
2024. Candidate access is an uncertain proxy. No current public opening or
physical entrance is verified by a leisure/access tag. The archived historical
pilot failed with HTTP 406 and establishes no temporal stability. No historical
requests were repeated in the offline rebuild.

Scientific weights, hybrid/fractional allocation, count versus composition,
shared eligibility, thermal threshold and local-inference family remain
provisional. Route policies are a separate family from the 16-scenario
factorial; no all-family joint robustness claim is made. No health, causal,
predictive-accuracy or policy-superiority claim is validated here. Original
independent acceptance/issue statuses are unchanged; QA-01 remains with the
Independent Re-audit.
