# Audit Evidence Index

All files are in this directory. The audit does not modify the manuscript or the
frozen RC1 artifact.

## Reports

| File | Purpose |
|---|---|
| `INDEPENDENT_SCIENTIFIC_AUDIT.md` | Full independent scientific assessment |
| `SCIENTIFIC_DECISION_RECOMMENDATIONS.md` | D1–D12/D13 recommendations |
| `QUANTITATIVE_REPRODUCIBILITY_AUDIT.md` | Independent calculations and Table 7 discrepancy |
| `LANDSAT_PROVENANCE_AUDIT.md` | RS-01 investigation |
| `PEER_REVIEW_SIMULATION.md` | Major/minor reviewer concerns |
| `PREPRINT_RELEASE_READINESS.md` | PASS/CONDITIONAL/HOLD gate assessment |
| `REVISION_PRIORITY_PLAN.md` | Ordered revision plan |
| `DECISION_MATRIX.csv` | Compact D1–D13 matrix |
| `REFERENCE_VERIFICATION.md` | 61 cited-reference verification and WorldPop/Landsat metadata |
| `POST_AUDIT_REVISION_STATUS.md` | What the current manuscript revision fixed and what remains |
| `FINAL_EDITORIAL_REPORT.md` | Final substantive editorial revision and PDF build |
| `FINAL_NUMERICAL_CONSISTENCY_CHECK.md` | Final numerical and reference checks |
| `FINAL_RESEARCH_DECISIONS.md` | Applied D1–D13 research specification |
| `AUTHOR_AND_RELEASE_CONFIRMATIONS.md` | Internal author/licence/release checklist |

## Scripts

| Script | Output |
|---|---|
| `scripts/independent_spatial_check.py` | `evidence/independent_spatial_check.json` |
| `scripts/independent_spatial_9999.py` | `evidence/independent_spatial_9999.json` |
| `scripts/independent_model_comparison.py` | `evidence/independent_model_comparison.csv` |
| `scripts/independent_rank_comparison.py` | `evidence/independent_rank_comparison_exact.csv` |
| `scripts/independent_score_check.py` | `evidence/independent_score_check.csv` |
| `scripts/independent_attribution_check.py` | `evidence/independent_attribution_comparisons.csv` |
| `scripts/independent_cutoff_check.py` | `evidence/independent_cutoff_check.json` |
| `scripts/independent_scenario_check.py` | `evidence/independent_scenario_jaccard.csv`, `independent_scenario_family_summary.csv` |

## Reproducibility notes

- Scripts use the RC1 integration virtual environment
  `D:\jakarta-heat-integration\.venv\rc1\Scripts\python.exe`
  (Python 3.12.10, pandas 3.1.1, geopandas 1.2.0, libpysal 4.15.1,
  esda 2.10.0).
- The LISA recomputation uses `libpysal.weights.Queen.from_dataframe`, not the
  project's STRtree fast path.
- The score/rank recomputation uses the documented p5–p95 normalisation and
  unclipped-score tie-break.
- No synthetic data were generated. No RC1 file was modified.
