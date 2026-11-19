# DM-01: demographic source support, version 1

This correction applies to 2,765 existing clipped master polygons. Original
`population_grid.csv`, `vulnerability_grid.csv`, `spatial_features.csv` and
`final_model_features.csv` are preserved byte for byte. Analytical replacements
are explicitly named `demographic_features_corrected.csv`,
`spatial_features_corrected.csv`, and `final_model_features_corrected.csv/.gpkg`.
They are an interface for DM-02, not an approved replacement scientific model.

The [WorldPop raster API documentation](https://api.worldpop.org/v3/documentation)
distinguishes NoData outside requested areas or without source values from
supported population zero. Source TIFFs identify 2024, Global2 R2025A, people per
cell, both sexes, ages 0–14 and 65+, CC BY 4.0, DOI 10.5258/SOTON/WP00841.
NoData is -99999 in the supplied rasters. NoData is not a demographic estimate.

The historical request masked age surfaces to the unbuffered five-city polygon.
The QGIS zonal hybrid sums centres if more than one valid centre exists,
otherwise uses fractional intersections. An empty sum was exported as zero.
The historic interactive action cannot be conclusively reconstructed; the empty
mask and numerical-zero pathway are directly reproducible. The new
`aggregate_demographics.py` implements that mechanism with **NaN for no valid
overlapping source pixels**. It does not replace a valid centre-supported zero.

`agent2_buffered_age.py` retrieved two real age surfaces for a bounding rectangle
covering the five-city union with a 1,000 m UTM buffer. Requests, response hashes,
retrieval UTC, and tags are archived in `data/raw/worldpop/age_buffered/`.
`buffered_source_compatibility.csv` verifies matching year/release/DOI/units/age
classes, integer pixel alignment, no lost valid pixels, and exact equality on
74,429 previously valid pixels **per raster**. Buffering adds support, not a new
age-share estimate. The new raster was not generated from population ratios.

The 19 original age-no-support IDs reconcile in
`demographic_support_reconciliation.csv` and `original_masks/`. Thirteen gain
actual source pixels; six remain unsupported in total and both ages:

```
JKT_R003_C031 JKT_R057_C063 JKT_R061_C009
JKT_R061_C010 JKT_R061_C011 JKT_R062_C043
```

All six have analytical nulls, with their original exported zeros retained as
`*_raw`. `JKT_R050_C061` has valid age support summing to zero under the hybrid
rule and total population approximately 0.00012; it remains a supported estimated
zero. The fractional sensitivity may allocate tiny positive ages there.

For each feature, `demographic_support.csv` contains integer overlapping-valid
pixel count; fractional valid-pixel count; projected support area in m²;
support-area / actual clipped polygon area; centre count; raster SHA-256; support
version; and two distinct states:

| Field | Values and meaning |
|---|---|
| `*_support_state` | `no_source_support`, `valid_estimated_zero`, `valid_uncertain_estimate` |
| `*_export_state` | `processing_empty_sum_zero` or `supported_source_export` describes the preserved historical export |

Fractional pixel weights use native EPSG:4326 intersection / source-pixel area;
support areas are reprojected to EPSG:32748 and intersected back with the actual
analysis geometry. This prevents projected chord approximation from assigning
support outside a tiny clipped cell. No area multiplier is applied to an already
aggregated people count. Support fraction measures spatial coverage, not
statistical certainty or census validation.

`person2_contracts.integrate_spatial(..., demographic_support=...)` requires
null exactly when valid support count is zero, rejects fabricated zero in an
unsupported cell, checks finite integer counts and matching states, and retains
all support columns. The legacy four-argument join still rejects undocumented
nulls and produces the audited baseline. Use both `--demographics` and `--support`
with `07_integrate_spatial.py`; its default output then becomes the **separate**
`spatial_features_corrected.csv`.

Vulnerable count uses ordinary addition so a missing age propagates. Composition
is undefined for missing/nonpositive total population. Model eligibility is a
separate decision: corrected common-set **proposal** is 2,536, against 2,538
audited baseline; original-mask null exclusion alone yields 2,526. Agent 3 must
consume these support states for DM-02; a downstream legacy loader that drops
them remains scientifically incomplete.

Verification: run `scripts/run_reproduction.ps1 -Scope Agent2`. Pixel fractions
are independently checked against exactextract for all grids, and separate union
extraction conserves fractional totals within 0.01 person (actual errors <0.00005).
Tests also exercise all-NoData, supported zero, partial pixels, invalid support,
source preservation, null joins, exact GIS geometry and the independent audited
baseline ranking. See `handoff/REMEDIATION_AGENT2.md` for actual run outcomes.
