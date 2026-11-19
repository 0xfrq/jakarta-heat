# BG-01: allocation and partial-cell sensitivity

Population inputs are modeled **people per source pixel**, not density. Master
polygons are a 500 m UTM lattice clipped to the five mainland cities. There are
383 partial polygons and 65 below 10% of 250,000 m²; the smallest is about
0.422885 m². None is removed from source delivery. `coverage_ratio` uses nominal
lattice area; demographic and thermal valid fractions use actual clipped area.

The original QGIS hybrid takes the sum of valid pixel centres when centre count
>1; otherwise it allocates intersecting valid pixels fractionally. It is
reproduced in executable code, including the correction that empty support
produces null. The alternative uniformly allocates each valid native raster
pixel by its polygon intersection fraction. Since EPSG:4326 cells have varying
metric area, fractional weights are calculated in the native raster plane;
this is the explicitly declared within-pixel uniform allocation assumption.
It does not claim to know subpixel residential distribution.

`aggregation_conservation.csv` compares the sum over disjoint grid allocations
with an independent exactextract extraction over their study union. All three
fractional totals pass 0.01-person absolute tolerance. The hybrid is **not
additive under changes of partition**: centres may be selected differently in
each polygon, so it is not labeled a conserved allocation. Its differences from
the fractional union are exported for all three variables. Buffered age masks
are used in the corrected comparison; original-mask results remain archived.

`partial_grid_scenarios.csv` retains every ID, actual area, coverage, count, and
fractional count, plus predeclared retained flags for coverage >=0, .1, .25, .5.
These are exploratory diagnostic thresholds chosen before reranking, not
outcome-optimized deletions. Exact dropped IDs and count changes are recoverable.
`remediation_model_scenarios.csv`, `changed_priority_grids.csv`, and
`remediation_scenario_ranks.csv` report top 5/10/20 budgets, retained/entered/left,
Jaccard and rank Spearman. Both eligibility-changing and same-ID rerankings are
exported; fixed comparisons recompute normalization on the identical common IDs.

Actual top-10% M4 results against audited baseline:

| Alternative | Eligible | Jaccard, changing set | Jaccard, fixed set |
|---|---:|---:|---:|
| Buffered source, hybrid | 2536 | .992157 | 1.000000 |
| Buffered source, fractional | 2536 | .881481 | .881481 |
| Buffered hybrid, coverage >=.1 | 2492 | .961089 | 1.000000 |
| Buffered hybrid, coverage >=.25 | 2447 | .926641 | 1.000000 |
| Buffered hybrid, coverage >=.5 | 2384 | .881679 | 1.000000 |
| Density objective, exploratory | 2536 | .902622 | .909774 |

Uniform fractional allocation swaps 16 cells at the M4 top-10% boundary. This
differs legitimately from the audited original-mask alternative (17 entrants):
source support was corrected first. A static figure and exact entrant/exit IDs
are delivered. Density is a different research objective; both population and
age counts are divided by actual clipped km² before log normalization in that
scenario. Tiny-area densities are uncertain; they are not substituted into
official count-oriented scores.

Recommendation: retain buffered hybrid as a continuity-oriented **proposal**,
show fractional conservation and rank sensitivity alongside it, and prefer
fractional allocation if additive count accounting is the agreed estimand.
Do not multiply these counts by coverage again. Retain partial cells with
support/area flags; any exclusion threshold and the primary allocation require
coordinator approval under MD-01/BG-01. No official baseline was changed.

City summaries assign complete clipped grids to their majority-area city. They
are not exact raster zonal totals within administrative boundaries. Separate
city-boundary aggregation would answer a different accounting question.
