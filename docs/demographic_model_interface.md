# DM-02 integration contract

RC1 update: the canonical candidate now consumes Agent 2 version
`agent2-DM-01-v1-buffered-age` from `data/processed/demographic_support.csv`
and `demographic_features_corrected.csv`. Six cells have unsupported total/age
estimates; 13 of the original 19 unsupported age cells have recovered source
support. `remediation_inputs/` below describes the preserved historical snapshot.
The authorized RC1 standard and expanded runs rebuild their respective output
directories; see `RC1_REPRODUCE.md` for the current contract and evidence.

Inputs remain read-only. Canonical `demographic_support.csv` must have exactly the same complete grid ID set as demographic features, unique IDs, a nonempty `support_version` on every row, and complete Boolean `qa_population_source_no_support` / `qa_age_source_no_support` flags. True/False or numeric 0/1 are accepted explicitly; unknown spellings/missing flags fail. Fractional support-pixel equivalents, state/provenance fields and raw values survive ingestion. The candidate input uses auditor support only, labelled `audit-2026-11-20-fractional-mask-v1-PROVISIONAL`; it is not Agent 2's completed DM-01.

Optional `demographic_features_corrected.csv` requires the same IDs/version and analytical `population`, `pop_child`, `pop_elderly`; nulls are valid and original feature exports are retained under `raw_*`. Conflicting support versions/flags fail rather than being overwritten. A compatible recovered-source support version must replace the provisional overlay; do not pair new recovered numbers with old no-support flags. Inline GIS support fields are also preserved by the analytical join.

Default locations are under the chosen input directory. Overrides: `JHIM_INPUT_DIR`, `JHIM_RS_PATH`, `JHIM_DEMOGRAPHIC_SUPPORT`, `JHIM_DEMOGRAPHIC_CORRECTED`. These are hashed, including absent fallbacks, and changing their selection invalidates saved-output freshness. No runtime sibling-worktree path is required. The standard pipeline still targets original directories; **use the separate remediation runner until the coordinator authorizes replacing the official baseline**.

Eligibility: M1 supported thermal QA; M2 additionally NDVI; M3 additionally supported total population; M4 additionally child/elderly, consistency and measured walking route (or explicitly declared stress assumption). Shared comparison uses M4 eligibility for all four models. Null/zero population gives undefined composition; share scenarios exclude it. All master IDs and reason codes remain in CSV/GIS.

Agent 2 scenario handoff must supply per-grid route versions with unique IDs, scenario ID, access/permission/connector policy, observed-vs-assumed metric label and provenance hashes. Do not hand over only aggregate Jaccards: these cannot be replayed at top 5/10/20 or joined into a joint scenario ensemble. Destinations and verified entrance evidence retain separate status fields; unknown access is never promoted to confirmed public access.
