# RC1 source and conflict record

The source branch tips matched the supplied commits before integration:

| Workstream | Full source commit |
|---|---|
| Agent 1 | `4f6c6797bfdd5148d7a91ef0f002bf6467edb04e` |
| Agent 2 | `e713342bf7c078d44c60e41da859d22a0fbc6218` |
| Agent 3 | `7ec9b2eaf42726991d8dbaad2c1db37bc7530151` |
| Main baseline | `f9b5c02ae2782ca00edcc077a29999b7ada3b91b` |

`integration/rc1` started from Agent 2. Merge `b936e81` includes Agent 1;
merge `498247e` includes Agent 3. Agent 1's earlier remote-sensing delivery commit
is also in its ancestry, so integration includes the actual exports, aggregation,
validation and original contract tests as well as the remediation commit.

Only `README.md` conflicted. Both Agent 2's handoff/limitations and Agent 3's
model/dashboard sections were retained. Agent 3's new dashboard and the renamed
prototype both remain. No source implementation was selected wholesale over a
conflicting implementation. Source branch tips and worktrees remained unchanged.

The integration fixes are separate from the merges. They select the revised A1
RS table, retain original measured LST/NDVI, preserve A2 raw columns and consume
its corrected demographics/support. Agent 3's historical fallback is retained
as an explicit historical mode; `--integrated` selects canonical inputs and
new versioned comparison lineage. Five A2 route versions are replayed by grid
ID, and aggregation sensitivity uses corrected A2 buffered data. Baseline
observed routes remain the provisional primary choice; integration does not
approve a different scientific policy.

The frozen Agent 3 code snapshot under Agent 2 QA evidence was renamed to
`.py.txt`, preserving its checkout bytes while making it non-importable. The
legacy integration stage now refuses execution and directs callers to RC1.
Runtime GIS helpers default to this workspace. Historical baseline capture and
handoff generators are archival utilities, outside the consolidated runtime lane.

The original audit in `D:/jakarta-heat/audit` and the local copy were hashed before
pipeline execution. The final verifier checks every original file against those
hashes. `/audit/` is ignored to preserve the separately supplied package without
mixing it with the candidate's new evidence. No original issue status or release
gate is edited by this integration.

Three archived park HTML checkouts differed from their frozen hashes solely by
newlines. Restore rejected them first. The reconciliation records both hashes
in `outputs/qa/rc1/frozen_checkout_repairs.json`, preserves the originals under
`dist/checkout_originals`, and restores the hash-verified bundle bytes. Artifact
paths now use `-text` in `.gitattributes` to prevent recurrence after checkout.
