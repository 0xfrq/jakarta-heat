# Source and Provenance

**Prepared:** 20 November 2026
**Manuscript status:** working preprint draft, scientific decisions pending

## 1. LaTeX template

| Item | Value |
|---|---|
| Template | Manuscript Multi-Target LaTeX Template |
| Author | Rodolfo Aramayo (Texas A&M University) |
| Version | v1.0.0, published 19 August 2026 |
| Zenodo record | <https://zenodo.org/records/22018962> |
| Template DOI | `10.5281/zenodo.22018962` (template, not this manuscript) |
| Upstream repository | <https://github.com/raramayo/Manuscripts_Templates_Latex> |
| Licence | GNU General Public License v3.0 or later (GPL-3.0-or-later) |
| Source archive used | `raramayo/Manuscripts_Templates_Latex-v1.0.0.zip` |
| Source archive SHA-256 | `815c28eeea8daa88f7874195a65ed264ee55c811d724f45b0fc05b0d0a91f877` |
| Extracted directory suffix | `raramayo-Manuscripts_Templates_Latex-2be6b6b` |
| Template `VERSION` file | `1.0.0` |

The template's class and bibliography style derive from Ricardo Henriques's
HenriquesLab bioRxiv template. That upstream attribution is retained in the
template's `docs/PROVENANCE.md`, `LICENSE`, and class header. The template is a
third-party typesetting resource, not an official Zenodo submission requirement
and not an endorsement by Zenodo or by the template author.

### Licence implications

The template source (class, bibliography style, build scripts and documentation)
is distributed under GPL-3.0-or-later. The template files retained in this
directory remain under that licence. The manuscript text, original figures,
tables and research registers are the project's scientific content; the GPL
applies to the template code, not automatically to the manuscript's scientific
prose. This is a provenance statement, not legal advice. Anyone redistributing a
modified version of the template files must comply with the GPL. The manuscript
does not relicense the template.

### Local adaptations (manuscript-level only)

The shared class is used unmodified. The manuscript preamble makes four
presentation-level adaptations for a one-column research article:

1. Conventional decimal section/subsection numbering, replacing the class's
   bioRxiv-style "Supplementary Note" heading.
2. One-column layout, overriding the class's default two-column start.
3. Normal-weight abstract and paragraph indentation for readability.
4. `booktabs`, `tabularx`, `threeparttable`, `seqsplit` and `float` for tables
   and long hashes.

These changes are in `input/Manuscript.tex` and `input/Supplementary.tex`, not
in `_Templates/`. The class and bibliography style remain the upstream v1.0.0
files.

## 2. Research artifact

| Item | Value |
|---|---|
| Project | Jakarta Heat Inequality Mapper |
| Frozen reference | RC1 |
| Artifact commit | `3b8ed05be92c35bbb2b3a617688540ee856b11c8` |
| Artifact tree | `2b312d673faac64d51559cf9612caf61847ad226` |
| Source-build commit (reported) | `f1e69a370f743985977e3d90c59179c76eea35d9` |
| Implementation SHA-256 | `6b2eae9dc37b14d92bd6accafda602da1e42af643ba8a72b6431d60e985b233e` |
| Primary evidence | `D:\jakarta-heat-auditor-rc1\audit\rc1_reaudit\` |
| Integration evidence | `D:\jakarta-heat-integration\handoff\RC1_HANDOFF.md`, `docs/integration_manifest.json`, `docs/RC1_REPRODUCE.md` |
| Analysis tables | `outputs/tables/`, `outputs/remediation/tables/`, `data/processed/modeling/` |

The manuscript uses RC1 as the frozen, audited reference. RC2 engineering or
remediation outputs were not substituted. The legacy 2,538-cell benchmark is
identified as legacy; the RC1 common comparison set is 2,536 cells.

## 3. Data sources and reference periods

| Source | Variable | Reference period | Native resolution | Processing | Main limitation |
|---|---|---|---|---|---|
| Landsat 9 Collection 2 Level-2 (USGS) | LST, NDVI, thermal QA | 2024 declared recipe period | 30 m | Clear-sky per-pixel median composite; QA\_PIXEL bits 0–5; QA\_RADSAT = 0; area-weighted zonal mean | Scene/task/AOI lineage unavailable (RS-01); surface not air temperature; seasonal representativeness unverified |
| WorldPop Global2 R2025A | Total population; ages 0–14, 65+ | 2024 reference year | ≈100 m (3 arc-second) | Modelled people per cell; hybrid or fractional zonal allocation | Model estimates, not census; six cells without age support; 383 partial cells |
| OpenStreetMap | Candidate park polygons | 2026-11-19 snapshot | Vector | 1,015 candidates; representative point; nearest graph node | 0 verified public access/entrances; 980 unknown; 1,015 unresolved |
| OpenStreetMap | Pedestrian graph | 2026-11-19 snapshot | Vector | Shortest path; 1,000 m cap; 226 missing baseline routes | Modelled, unvalidated routes; 167 origin + 78 park connector conflicts; 407 missing under conservative policy |
| Administrative boundaries | Five mainland city polygons | Study definition | Vector | 500 m UTM lattice clipped to land | Kepulauan Seribu excluded; boundary vintage not independently audited |

The analysis is a **mixed-period candidate proxy**: 2024 thermal/demographic
patterns combined with a 2026 candidate park/network snapshot. It is not a
verified 2024 access reconstruction and not a 2026 heat estimate.

## 4. Figure provenance

All main and supplementary figures were generated for this manuscript from the
frozen RC1 tabular and GIS sources. No synthetic data were introduced. The
generator is `scripts_paper/make_figures.py` (kept for reproducibility; it reads
only the frozen RC1 files and writes PDF/PNG copies). The numerical extracts used
for the text are in `scripts_paper/manuscript_numbers.json`; the verified
bibliographic metadata probes are in `scripts_paper/crossref_metadata.json` and
`scripts_paper/s2_metadata.json`.

| Figure | Source | Notes |
|---|---|---|
| Fig. 1 | `merged_grid.csv`, `priority_models.csv`, `grid_500m_jakarta.gpkg` | LST and NDVI, common sample |
| Fig. 2 | same | Population and capped park distance |
| Fig. 3 | same | M1/M4 top-decile maps |
| Fig. 4 | `priority_models.csv` | Rank displacement |
| Fig. 5 | `rank_change_attribution.csv`, `robustness_family_summary.csv` | Shapley shares and family envelope |
| Fig. 6 | `lisa_m4_primary.csv`, `lisa_tail_permutation_sensitivity.csv` | LISA map and convention counts (two-sided/9,999/BH) |
| Fig. S1 | `priority_models.csv` | Score distributions |
| Fig. S2 | `eligibility_by_model.csv`, grid | Exclusion geography |
| Fig. S3 | `parks_jakarta.gpkg`, `park_access_evidence.csv`, grid | Candidate parks and missing routes |

Figure captions state the source, model/sample version and limitations. Maps use
a common extent and explicit "excluded" categories; they are not dashboards or
screenshots.

## 5. Table provenance

Tables 1–11 and S1–S9 are generated from RC1 tables or assembled from the
manuscript's own literature review. Every numerical table is traceable to the
files listed in `FIGURE_TABLE_REGISTER.md` and `CLAIM_EVIDENCE_MATRIX.csv`.
Table 1 (literature comparison) contains citations, not new numerical results.
The machine-readable supplementary files are in
`input/Supplementary_Tables/`.

## 6. Build environment

| Item | Value |
|---|---|
| OS | Windows x64 |
| TeX distribution used | TinyTeX / TeX Live 2026 (portable) |
| pdfTeX | 3.141592653-2-1.40.29 (TeX Live 2026) |
| latexmk | 4.88 (John Collins, 9 March 2026) |
| BibTeX | 0.99e (TeX Live 2026) |
| Template class | `_Templates/MultiTargetManuscript.cls` v1.0.0 |
| Bibliography style | `_Templates/MultiTargetManuscript.bst` |

The system MiKTeX 25.12 installation was also inspected. Its dependency
preflight hung on missing-package lookups, and `siunitx` loading stalled under
MiKTeX. The portable TinyTeX distribution compiled the template and manuscript
without that failure. This is documented rather than hidden. The exact commands
and warnings are in `COMPILATION_REPORT.md`.

## 7. What is not claimed

No manuscript DOI has been assigned. No Zenodo upload has been made. No claim of
peer review, acceptance, publication, verified public park access, verified 2024
Landsat acquisition, health impact, intervention effectiveness or Jakarta-wide
representativeness is made. The RC1 artifact is an internal, conditionally
released research candidate, not a public data release.
