# Agent 1 remote-sensing delivery after remediation

Date: 2026-11-20 WIB. Authoritative tasks: **RS-01 (P1)** and **DW-01 (P2)**
in the independent auditor's issue register. RS-02 belongs to Agent 3; this
workstream supplies support evidence. Numerical delivery and scientific acceptance
are separate. No independent audit gate is closed by this implementation log.

| Component | Evidence/status | Permitted interpretation |
|---|---|---|
| Required LST/NDVI (R2) | COMPLETE local numerical delivery: 2,765 measured grid rows; zero missing | Mean over valid pixel area of per-pixel clear-sky morning temporal-median LST, and similarly aggregated NDVI |
| Historical acquisitions (RS-01) | BLOCKED: scene/date/task/AOI archive unavailable, GEE authentication absent | 2024 is the declared recipe period; local arrays do not verify every original acquisition |
| Annual clear support | Available: grid mean 5.96–27.4 observations/pixel; pixel counts 3–28 | Unequal temporal sampling; counts do not identify dates or seasons |
| Monthly/seasonal support | BLOCKED pending new GEE export or historical acquisition archive | No seasonal-balance or annual-representativeness claim |
| DW median probabilities | Delivered for 2,764 cells; one tiny cell lacks source support | Median class probabilities, not categorical land-cover area |
| DW categorical fractions (R3) | **PARTIAL**, supplementary to current M1–M4; export absent | No measured tree/grass/built-area claims; all fraction fields remain null |
| Supplementary R3 scope decision | Proposed deferral; **not signed** | Coordinator must approve deferral and dependent claim removal, or retain and obtain an actual label export |

The current M1–M4 RS contract is `lst_c, ndvi` (`jhim/config.py`); categorical
DW fractions are absent from the model equations. Defer R3 for this primary study
as the preferred recommendation: this preserves the actual question and avoids
claiming information that was never exported. Retaining R3 is defensible for a
separate categorical-area analysis, but needs GEE, actual label intersections,
and manifest evidence before it can be marked complete. Probability features
cannot substitute for a label export. This recommendation awaits team approval.

## Baseline and revised data

The audited `data/processed/remote_sensing_grid.csv`, `.gpkg`, `.meta.json` and
both source GeoTIFFs remain unchanged. Their hashes are recorded in
`remote_sensing_export_manifest.json`. Revised local outputs are explicitly in
`data/processed/remote_sensing_remediated/remote_sensing_grid.{csv,gpkg,meta.json}`.
This is a proposed input revision for integration, not a silently changed model.

The revised table has 42 columns. Its original 30 columns retain order. Every
original value except `qa_area_km2` is identical to the audited CSV. The 383 clipped
cell areas now retain additional precision; the smallest positive area is
0.422884536660195 m² = 4.22884536660195e-7 km², instead of zero. Added
`qa_area_m2` retains projected geometry area. LST/NDVI/probabilities/flags and
eligibility inputs do not change. No current model score or rank change is induced
by these corrections when IDs and scientific configuration remain fixed.

## Categorical denominator contract (implemented, actual export still absent)

Let A be the clipped grid polygon area, V the valid-label area, and C_k the
pixel-intersection area assigned to class k by the per-pixel temporal mode.

- `*_fraction = C_k/A`, measured only when V > 0.
- `*_fraction_valid = C_k/V`, conditional on observed label support.
- `dw_label_valid_fraction = V/A`; `dw_label_missing_fraction = 1 - V/A`.
- All **nine** class fractions, including `snow_ice_fraction`, sum to V/A.
  Conditional fractions sum to 1. Snow/ice is retained even if unexpected locally.
- If V = 0 in an available label raster, class fractions are null, valid support
  is 0, and missing area is 1. Absence of the entire label export makes all of
  these fields null, because support has not been measured.
- An observed absent class has 0 only where at least one label exists. Unknown
  land-cover area is never redistributed or set to an observed class.

The previous code directly assigned exactextract's valid-support `frac` to a
whole-cell-area column. A half-supported cell would have reported tree/built as
0.5/0.5 instead of 0.25/0.25, obscuring 0.5 unknown area. Tests now check this
case, fractional overlaps, zero support, all nine classes and invalid codes.
No real categorical before/after change can be measured yet: no label raster
exists. The optional GEE script now explicitly aligns its grid to the frozen
probability raster and explicitly resolves modal ties to the lowest class code.
It has syntax verification only; GEE execution remains untested.

## Thermal QA evidence supplied to Agent 3 (RS-02)

`outputs/qa/rs_temporal_support.csv` contains annual support for every master ID;
`outputs/qa/agent1_remediation/independent_pixel_checks.csv` contains 140 independent
Shapely pixel intersections across 35 cells, including the four eastern gaps and
six smallest cells. JKT_R037_C062 independently has 6,724.1312 m² valid LST area
out of 24,223.1114 m² (27.7591557%). Its clipped/nominal-grid area is 9.6892445%,
a different denominator. Delivered LST 42.234 °C and NDVI 0.2961 are preserved.

| Exploratory support policy | All RS-eligible grids | With legacy observed route |
|---|---:|---:|
| Baseline valid LST area >= 0.50 | 2,764 | 2,538 |
| Valid LST area >= 0.25 | 2,765 | 2,539 |
| Include measured values, retain flags | 2,765 | 2,539 |
| Existing strict `rs_qa_ok` | 2,752 | 2,527 |

These are support-only scenarios, before Agent 2 corrected demographic support.
`rs_qa_policy_support.csv` provides every ID and policy membership. Retaining
the audited 0.50 policy provisionally and publishing relaxed/strict alternatives
is preferable until the team signs its primary QA rule. A 0.25 cutoff restores
one measured cell but offers less spatial support; strict QA removes 11 additional
route-present cells but ST_QA is retrieval QA, not uncertainty of the composite.
No threshold is empirically validated by this exercise. Agent 3 must calculate
fixed-non-RS eligibility, normalization/rank/top 5/10/20 effects and final
reason codes; this workstream does not sign that scientific model decision.

## Temporal estimand decision (TM-01 dependency)

Prefer a mixed-period exploratory proxy study: the declared 2024 environmental
composite with the separate 2026 OSM proxy. Bound the thermal interpretation to
the existing clear-sky morning temporal median. This needs no invented seasonal
weights and preserves the baseline, but does not support actual annual exposure,
current 2026 thermal conditions, or contemporaneous 2024 accessibility effects.
If stronger annual representativeness is retained, recover monthly support and
compare defensible season/season-balanced composites using Agent 3 fixed models.
The effect of seasonal reweighting is currently **unknown**, not zero.

Official references checked for the remediation:
[Landsat C2 L2 collection/scaling](https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC09_C02_T1_L2),
[DW label/probability semantics](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1),
[explicit export grid alignment](https://developers.google.com/earth-engine/apidocs/export-image-todrive).
These specify the intended algorithm; they do not authenticate the original run.
