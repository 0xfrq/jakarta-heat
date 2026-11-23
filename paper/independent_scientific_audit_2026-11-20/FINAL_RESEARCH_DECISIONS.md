# Final Research Decisions

**Manuscript:** From Thermal Hotspots to Spatial Priorities: Attribution and
Sensitivity of Urban Heat Screening in Jakarta
**Date:** 21 November 2026
**Status:** editorial research specification applied to the manuscript.
**Important:** this document records the decisions used to prepare the
publication candidate. It is **not** a signed author-consent record, peer-review
record or public-release authorization.

## D1 — Temporal interpretation

**Applied:** mixed-reference-period spatial screening study.

- Landsat thermal/vegetation processing is configured for the 2024 calendar year
  and described as a declared 2024 processing period.
- WorldPop is the 2024 reference-year modelled population.
- OpenStreetMap parks and network are a November 2026 extraction.

The paper does not describe the combined data as a verified historical snapshot
of Jakarta in 2024. Temporal incompatibility is stated once in Data and once in
Limitations.

## D2 — Historical OSM reconstruction

**Applied:** not performed and not simulated. The study is a mixed-period
screening comparison, not a longitudinal analysis. Missing 2024 access is a
limitation, not a fabricated scenario.

## D3 — Demographic source support

**Applied:** preserve missingness.

- 2,765 master grid IDs retained.
- 13 recovered age-support cells.
- Six cells remain unsupported; analytical values remain null.
- Original source zeros are retained only as raw archival attributes.
- M4 common comparison excludes the six unsupported cells.

## D4 — M4 scientific construct

**Applied:** retain the original numerical model and relabel it as an
**exploratory heat–population–park-deficit screening index**.

M4 is not presented as a validated epidemiological heat-risk index, an
age-composition vulnerability index, a verified public-park accessibility index,
a causal explanation or an intervention-effectiveness model. M1–M4 formulas,
weights, scores and rankings are unchanged.

## D5 — Age vulnerability

**Applied:** vulnerable-person **count** in the reported model; vulnerable
**share** as sensitivity analysis.

The paper states that counts and shares answer different questions. The
near-collinearity with total population is reported as an empirical finding,
not as evidence that age is unimportant. The count-to-share sensitivity is
reported rather than silently replacing the primary score.

## D6 — Population allocation

**Applied:** hybrid allocation remains the empirical baseline; area-fractional
allocation is reported as a robustness alternative.

The paper states that fractional allocation is preferable for additive
population accounting and that the hybrid rule is not additive under
repartitioning. The observed 16-cell top-set swap and Jaccard 0.881 are
reported.

## D7 — Thermal coverage

**Applied:** 50% valid-pixel threshold retained for the reported analysis.
`JKT_R037_C062` retains its delivered satellite values but is excluded as a
quality decision; its 27.759% valid-LST support is disclosed. The threshold is
described as a quality-control choice, not as validated truth.

## D8 — Park accessibility

**Applied:** modelled network accessibility to OpenStreetMap candidate parks.

- Candidate-park terminology is used throughout.
- Representative-point routing is described.
- No-route values remain missing, not zero.
- Conservative connector and positive-tag-only scenarios are reported as stress
  tests, not ground truth.
- No claim of verified public access, verified entrances or actual walking
  access is made.

## D9 — Analysis population

**Applied:** common 2,536-cell sample for M1–M4 comparisons.

- 2,765 master cells.
- 229 excluded from the common comparison.
- 2,536 common eligible cells.
- 2,535 spatially tested cells after excluding the Queen island
  `JKT_R013_C019`.

The paper reports the exclusion profile and does not generalise conditional
comparisons to every grid in Jakarta.

## D10 — Spatial inference convention

**Applied:** **two-sided local Moran testing, 9,999 permutations,
Benjamini–Hochberg correction at q = 0.05** as the adopted primary reporting
specification.

Rationale: there is no sufficiently established directional local hypothesis;
both positive clusters and spatial outliers matter for interpreting the map;
9,999 permutations provide finer attainable p-value resolution; BH gives an
interpretable primary multiplicity adjustment with dependence assumptions
acknowledged. BY is retained as a more conservative sensitivity check.

Verified primary counts:

- Two-sided / 9,999 / BH: **493 significant cells** (HH 252, LL 227, HL 7,
  LH 7; 2,042 not significant).
- Two-sided / 999 / BH: 496.
- Directed / 999 / BH (historical): 663.
- Directed / 9,999 / BH: 687.
- Directed / 999 / BY: 0.
- Directed / 9,999 / BY: 284.
- Two-sided / 9,999 / BY: 234.

The primary map is built from per-cell outputs in
`input/Supplementary_Tables/lisa_m4_primary.csv`. The convention is described
as adopted during an exploratory analysis, not as preregistered.

## D11 — Dynamic World

**Applied:** categorical land-cover fractions deferred. The reported M1–M4
equations do not use them; no class-fraction or categorical-area claim is made.

## D12 — Scientific contribution and novelty

**Applied:** attribution and sensitivity of spatial priorities.

The contribution is:

- quantifying spatial reprioritisation across screening models;
- attributing M3-to-M4 change to park addition, age substitution and
  reweighting;
- showing the redundancy between vulnerable-person counts and total population;
- demonstrating the observed mathematical threshold behaviour of the additive
  park-deficit term;
- characterising sensitivity to accessibility, eligibility and demographic
  definitions;
- explaining the limits of interpreting composite priority maps.

The paper does not claim the first integrated framework, objective M4
superiority, a new causal mechanism or a validated health/policy model.

## D13 — Public release

**Applied:** clean Zenodo preprint package prepared, but no upload, submission,
publication or DOI request. The coordinator confirmed author metadata,
corresponding author, collective contributions, no external funding, no
competing interests, CC BY 4.0, and acceptance of the restricted Landsat
interpretation. Manual record review and upload remain. No DOI may be claimed
before Zenodo assigns one.

## Decision status table

| ID | Applied specification | Manuscript status | Human confirmation |
|---|---|---|---|
| D1 | Mixed 2024/2026 reference periods | Applied | Needed for scope |
| D2 | No historical OSM reconstruction | Applied | Needed for scope |
| D3 | Preserve null/no-support semantics | Applied | Formal |
| D4 | Exploratory heat–population–park screening index | Applied | Author/PI |
| D5 | Count primary; share sensitivity | Applied | Author/PI |
| D6 | Hybrid baseline; fractional sensitivity | Applied | Author/PI |
| D7 | 50% valid-pixel threshold | Applied | Author/PI |
| D8 | Candidate-park network proxy | Applied | Author/PI |
| D9 | 2,536 common comparison cells | Applied | Author/PI |
| D10 | Two-sided/9,999/BH primary LISA | Applied | Author/PI |
| D11 | Dynamic World categorical deferral | Applied | Author/PI |
| D12 | Attribution/uncertainty contribution | Applied | Author/PI |
| D13 | No public release yet; package built | Applied | Manual upload/review |
