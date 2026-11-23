# Zenodo Metadata Draft

**Status:** DRAFT ONLY — DO NOT UPLOAD
**DOI:** **NOT ASSIGNED**
**Release readiness:** **HOLD** until scientific approval and final verification

This file prepares metadata for a possible Zenodo preprint deposit. It does not
create a record, reserve a DOI or publish anything. All fields marked
`[HUMAN DECISION]` require the coordinator's written approval.

## 1. Basic fields

| Field | Draft value |
|---|---|
| Title | From Thermal Hotspots to Spatial Priorities: Attribution and Sensitivity of Urban Heat Screening in Jakarta |
| Resource type | Publication / Preprint (select the closest current Zenodo interface option) |
| Language | English |
| Version | `0.1.0-draft` (not a final release) |
| Publication date | Not set; do not use a future date as if published |
| DOI | **NOT ASSIGNED** |
| Access | Open access recommended, subject to human approval and third-party licences |
| License recommendation | **CC BY 4.0** for the manuscript text and original figures, subject to human approval. Do not apply a single licence to third-party data or to the GPL template files. |
| Rights holder | The three named authors / Renaro Lab, subject to written confirmation |

## 2. Creators and affiliation

| Order | Name | Affiliation | Email | ORCID |
|---:|---|---|---|---|
| 1 | Muhammad Fariq Faqih | Renaro Lab, student-led independent AI laboratory, <https://renaro.my.id> | `fariq@renaro.my.id` | Not supplied |
| 2 | Muhammad Alim Mustofa | Renaro Lab, student-led independent AI laboratory, <https://renaro.my.id> | `alim@renaro.my.id` | Not supplied |
| 3 | Mu'adz Abdulloh | Renaro Lab, student-led independent AI laboratory, <https://renaro.my.id> | `muadz@renaro.my.id` | Not supplied |

Corresponding author: currently Muhammad Fariq Faqih. **`[HUMAN DECISION]`**
confirm or change.

## 3. Description / abstract

Use the manuscript abstract, with the draft-status caveat retained until
scientific approval. Suggested deposit description:

> Urban heat mitigation planning increasingly relies on composite spatial
> indices that combine land surface temperature, vegetation, population and
> access to green space. Such indices produce priority maps, but the maps are
> model outputs rather than observed inequalities, and their dependence on
> demographic and accessibility assumptions is rarely quantified. We examine how
> spatial priorities change across four screening models in the five mainland
> administrative cities of Jakarta, Indonesia, on a 500 m grid (2,765 cells).
> The common comparison sample contains 2,536 cells. Thermal and demographic
> inputs refer to a declared 2024 period; the park and pedestrian-network
> snapshot is from 19 November 2026, so the analysis is a mixed-period candidate
> proxy. M1 and M4 share 38.4% of their top-decile cells; the mean absolute
> rank shift is 307 positions. Between M3 and M4, an exact three-factor Shapley
> decomposition attributes 85.5% of absolute rank movement to park addition,
> 13.2% to reweighting and 1.3% to the age-count substitution. The age count is
> nearly collinear with total population (Spearman rho = 0.9995); a count swap
> leaves the top decile almost unchanged (Jaccard 0.977), while a share swap
> changes it substantially (0.347). Under the provisional additive M4, the
> top-decile cutoff (0.8737) exceeds the maximum score of all 537 common cells
> within 500 m of a candidate park (0.8696); no near-park cell enters the top
> 254. This is a property of the index and observed inputs, not evidence that
> parks are unimportant. Access assumptions matter: a positive-tag-only
> destination stress test yields Jaccard 0.420, while a conservative connector
> scenario yields 0.896. The 229 excluded cells are cooler, greener and more
> peripheral than included cells; the common sample is a conditional estimand,
> not a Jakarta-wide estimate. Local Moran labels are convention-sensitive
> (663 significant under directed/999/BH, 496 under two-sided, 0 under BY/999,
> where the minimum attainable p-value exceeds the correction threshold). We
> make no claim about health outcomes, verified public park access, 2024
> historical network conditions or intervention effectiveness. The contribution
> is an attribution and uncertainty audit of a reproducible screening index,
> including negative findings about age-count redundancy and the mechanical
> behaviour of an additive park-deficit term.

Do not remove the draft banner from the PDF before approval. Do not present the
draft as peer-reviewed.

## 4. Keywords

- urban heat
- land surface temperature
- environmental inequality
- park accessibility
- composite index
- sensitivity analysis
- spatial autocorrelation
- Jakarta
- reproducibility

## 5. Related works

| Relation | Identifier | Note |
|---|---|---|
| Is supplement to / uses | Manuscript Multi-Target LaTeX Template v1.0.0, DOI `10.5281/zenodo.22018962` | Third-party typesetting template; GPL-3.0-or-later; not a Zenodo endorsement |
| Is related to | Jakarta Heat Inequality Mapper RC1 artifact, commit `3b8ed05be92c35bbb2b3a617688540ee856b11c8` | Internal research artifact; **no public DOI assigned**; do not invent one |
| Cites / uses | WorldPop R2025A, DOI `10.5258/SOTON/WP00841` | CC BY 4.0; modelled population |
| Cites / uses | Landsat 9 Collection 2 Level-2 product guide (USGS URL) | Official product documentation |
| Cites / uses | OpenStreetMap snapshot, 2026-11-19 | ODbL; attribution required |

Do not list a manuscript DOI, a Zenodo record, or a "submitted to" statement
until one exists.

## 6. Funding and acknowledgements

- Funding: **none verified**. Do not invent a grant.
- Acknowledgements: template attribution and open-source data/software
  acknowledgements are in the manuscript. Add only verified institutional or
  personal acknowledgements.
- Conflicts of interest: placeholder "none declared" pending written
  confirmation from all authors.

## 7. Files to deposit (if approved)

| File | Role | Notes |
|---|---|---|
| `Manuscript-zenodo.pdf` | Main preprint PDF | 23 pages; Zenodo footer profile |
| `Supplementary-zenodo.pdf` | Supplementary PDF | 6 pages |
| `Manuscript.tex` | Canonical LaTeX source | Required for reproducibility |
| `References.bib` | Bibliography | 61 verified entries |
| `Figures/` | Figure files | PDF and PNG |
| `Tables/` | Table fragments | LaTeX |
| `README.md`, `SOURCE_PROVENANCE.md`, `COMPILATION_REPORT.md` | Provenance | Include if the deposit is a full bundle |
| `CLAIM_EVIDENCE_MATRIX.csv` | Traceability | Include as supporting metadata |

Do **not** deposit the GPL template files as if they were the manuscript's own
work without retaining the GPL licence and attribution. If the bundle includes
`_Templates/`, include `LICENSE` and `SOURCE_PROVENANCE.md`.

## 8. Pre-deposit checklist

- [ ] **Verify Table 7/8 split**: M3-relative incremental effects (Table 7) and
      M4-relative construct/ablation comparisons (Table 8); check captions,
      footnotes and text.
- [ ] All three authors approve the author list, order, affiliation, emails and
      corresponding author.
- [ ] All three authors approve the Author Contributions statement.
- [ ] Coordinator signs the scientific decisions D1–D12 (or the approved
      subset), especially M4 construct, weights, support threshold, common set
      and LISA convention.
- [ ] RS-01 lineage is recovered or a written claim restriction is signed.
- [ ] Park access/entrance claims remain unverified and are labelled as such.
- [ ] Clean-checkout test and receipt portability are fixed, or the limitation
      is disclosed in the deposit.
- [ ] No manuscript DOI is invented; let Zenodo assign one only after upload.
- [ ] Licence choice is approved by all authors and is compatible with
      third-party data/template licences.
- [ ] Final independent re-audit is complete.
- [ ] A final PDF is rebuilt from the approved source and visually checked.

## 9. Explicit non-actions

No upload was performed. No DOI was requested or reserved. No record was
created. No claim of submission, acceptance, peer review or publication is made.
