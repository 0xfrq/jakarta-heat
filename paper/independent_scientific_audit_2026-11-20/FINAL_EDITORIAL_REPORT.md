# Final Editorial Report

**Manuscript:** From Thermal Hotspots to Spatial Priorities: Attribution and
Sensitivity of Urban Heat Screening in Jakarta
**Date:** 21 November 2026
**Prepared by:** Lead academic editor / LaTeX manuscript author
**Status:** final Zenodo package prepared; author metadata confirmed by the
coordinator; manual upload remains.

## 1. Editorial objective

The revision converted the manuscript from an audit-aware working draft into a
coherent research article. The scientific claims, model formulas and empirical
numbers remain tied to the processed RC1 data. The editorial work removed
project-management language, reduced repeated defensive caveats, shortened the
abstract, separated the two attribution baselines, updated the primary LISA
convention, and produced distinct clean and internal-review PDFs.

## 2. Substantive scientific changes

### 2.1 Jaccard interpretation

The previous wording treated 141/254 as a 38.4% overlap. The revision states:

- 141 shared of 254 = **55.5% retention**;
- union = 367;
- Jaccard = **0.384**;
- 113 cells unique to each set.

The correction appears in the Abstract, Results, Discussion, Conclusion and the
Table 6 note. Table 6 now reports shared counts and retention for all model
pairs.

### 2.2 Attribution tables

Table 7 and Table 8 are now separate:

- **Table 7**: incremental effects relative to M3 (reweighting 0.961, age 0.984,
  park 0.490, full M4 0.411).
- **Table 8**: construct/ablation comparisons relative to M4 (park addition
  0.861, reweighting 0.423, age 0.419, park-only 0.028, equal-weight 0.868).

The text explains that the two baselines answer different questions. The
Shapley shares remain 85.46% park, 13.25% reweighting and 1.29% age.

### 2.3 LISA primary convention

The adopted primary specification is now **two-sided local Moran, 9,999
permutations, Benjamini–Hochberg q = 0.05**. The M4 map and Table 10 were
rebuilt from per-cell outputs, not from aggregate totals.

Verified primary counts: **493 significant cells** (HH 252, LL 227, HL 7, LH 7;
2,042 not significant). The historical directed/999/BH configuration (663) and
the other alternatives (496, 687, 0, 284, 234) remain in the sensitivity table.
The zero under BY/999 is described as a resolution artifact, not as evidence of
no clustering.

### 2.4 M4 interpretation

M4 is described as an **exploratory heat–population–park-deficit screening
index**. The paper no longer calls it a provisional or validated vulnerability
model. It preserves the original formulas and weights and retains the
near-collinearity and mechanical-threshold findings.

### 2.5 Engineering language

The scientific narrative no longer contains the working-draft banner, RC1/RC2
release-gate language, "unsigned" status, or a claim-evidence register as a
substitute for evidence. The Data and Code Availability section now describes
the processed outputs, the separate raw bundle, source licences and the
reproducibility note concisely. RC2 engineering details are retained in the
technical evidence files and the internal audit record.

## 3. Language and presentation

- Abstract shortened from a verification-style summary to a coherent research
  abstract (about 260 words).
- Introduction contribution paragraph rewritten from a formulaic four-point
  list to a continuous argument.
- Repetitive caveats reduced; the remaining qualifications are tied to specific
  results or limitations.
- Author affiliation simplified to **Renaro Lab, Indonesia**, with the
  laboratory URL; the promotional "student-led independent AI laboratory"
  description was removed from the publication PDF.
- First author is the confirmed corresponding author on the clean PDF
  (`fariq@renaro.my.id`).
- No invented ORCID, funding, conflict or CRediT statement appears in the
  publication PDF. The funding and competing-interest statements reflect the
  coordinator confirmation; no individual CRediT roles were invented.
- The clean candidate uses the neutral template profile; no Zenodo footer label
  or deposit claim.
- The internal-review PDF is a separate wrapper with a concise internal
  identifier.

## 4. References

All cited references were checked against DOI or dataset records. The USGS
reference was corrected to the Landsat 8–9 Collection 2 Level-2 dataset DOI
`10.5066/P9OGBGM6`. WorldPop was verified as R2025A v1, 3 arc-second
(approximately 100 m), University of Southampton, 2025, DOI
`10.5258/SOTON/WP00841`. The compiled manuscript has 67 cited references.

## 5. Supplement

The supplement now contains S1–S9:

- data quality and missingness;
- three-budget scenario-family sensitivity;
- city composition;
- LISA summaries (historical and adopted primary);
- exclusion/score/park maps;
- all 49 executed scenario comparisons;
- six demographic no-support cells;
- eligibility reconciliation;
- figure/table provenance and machine-readable file list.

The primary LISA per-cell labels are in
`input/Supplementary_Tables/lisa_m4_primary.csv`.

## 6. Build and inspection

Built with TinyTeX / TeX Live 2026, pdfTeX 1.40.29, latexmk 4.88, using the
template's neutral profile. See `COMPILATION_REPORT.md` for commands, hashes and
warnings. The clean candidate is 25 pages; the internal review is 25 pages; the
supplement is 8 pages. The title page, declarations, attribution tables, LISA
figure/table, references and supplement pages were rendered and inspected. No
undefined citations or references remain. The public PDF contains Author
Contributions, Funding, Conflicts of Interest, Data and Code Availability,
AI-assisted tools disclosure, the CC BY 4.0 statement, and the template
attribution.

## 7. Remaining scientific limitations

The publication candidate retains:

- the declared rather than independently verified 2024 Landsat processing
  period;
- the mixed 2024 thermal/demographic and 2026 OSM reference periods;
- unverified public park access and entrances;
- modelled, unvalidated walking routes and missing-route values;
- six unsupported demographic cells;
- partial coastal grids;
- conditional 2,536-cell common sample;
- explicit modelling weights and park cap;
- LISA convention sensitivity;
- no health, causal or intervention-effectiveness claim.

These are substantive limitations, not editorial defects.

## 8. Release status

**ZENODO PACKAGE READY - AWAITING MANUAL UPLOAD.** The manuscript is not
peer-reviewed, not accepted, not deposited and has no DOI. Author metadata and
declarations are confirmed by the coordinator; no upload or submission was
performed.
