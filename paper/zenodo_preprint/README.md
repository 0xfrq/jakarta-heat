# Jakarta Heat Inequality Mapper â€” Zenodo Preprint Workspace

**Status:** `WORKING PREPRINT DRAFT â€” SCIENTIFIC MODEL DECISIONS PENDING`
**Branch:** `paper/zenodo-draft`
**Base research revision:** `3b8ed05be92c35bbb2b3a617688540ee856b11c8`

This directory contains the canonical LaTeX manuscript, bibliography, figures,
tables, supplementary material and traceability registers for the Jakarta Heat
Inequality Mapper preprint. The manuscript is written in formal academic English.
Project handoff notes are in Indonesian.

## Author and affiliation

- Muhammad Fariq Faqih â€” `fariq@renaro.my.id`
- Muhammad Alim Mustofa â€” `alim@renaro.my.id`
- Mu'adz Abdulloh â€” `muadz@renaro.my.id`

Affiliation: **Renaro Lab**, student-led independent AI laboratory,
<https://renaro.my.id>.

ORCIDs are not included because none were supplied. The manuscript lists all
three e-mail addresses in the correspondence line and does not assert a single
corresponding author without an explicit team decision.

## Canonical source

The single canonical manuscript source is:

```text
input/Manuscript.tex
```

The bibliography is `input/References.bib`. Figures are in `input/Figures/`;
tables are in `input/Tables/`. `input/Supplementary.tex` is a separate,
standalone supplement. Do not create a second copy of the manuscript elsewhere.

## Build

The template is the **Manuscript Multi-Target LaTeX Template v1.0.0** by Rodolfo
Aramayo (Zenodo DOI `10.5281/zenodo.22018962`, GPL-3.0-or-later). The shared
class and bibliography style are in `_Templates/`; the upstream build driver is
`build.sh`.

On this Windows machine, the system MiKTeX installation was unusable for the
template's dependency preflight (its package installer/`kpsewhich` calls hung).
A portable **TinyTeX / TeX Live 2026** distribution was used instead. The
commands below are the ones actually executed:

```bash
export PATH="/c/Users/VICTUS/AppData/Local/Temp/opencode/TinyTeX/TinyTeX/bin/windows:$PATH"
export BASH="$(command -v bash)"
cd /d/jakarta-heat-paper/paper/zenodo_preprint

./build.sh --target neutral --input-dir input --main Manuscript.tex
./build.sh --target neutral --input-dir input --main Manuscript-internal.tex
./build.sh --target neutral --input-dir input --main Supplementary.tex
```

The neutral profile is used for the publication candidate so the footer does not
imply a Zenodo deposit. A convenience wrapper that builds the candidate, internal
review and supplement PDFs is `scripts_paper/build_final_candidate.sh`.

If TeX Live is available on another machine, the same commands work without the
TinyTeX `PATH` export. `make TARGET=zenodo INPUT_DIR=input MAIN_TEX=Manuscript.tex`
is equivalent when `make` and Bash are available.

## Outputs

```text
output/pdf/Manuscript-submission-candidate.pdf    # 25 pages, neutral profile
output/pdf/Manuscript-internal-review.pdf         # 25 pages, internal identifier
output/pdf/Supplementary-submission-candidate.pdf # 8 pages
output/pdf/Manuscript-zenodo.pdf                  # historical profile build
output/pdf/Manuscript-neutral.pdf                 # neutral build source
output/pdf/Supplementary-zenodo.pdf               # historical supplement build
```

The compiled PDFs were rendered and visually checked. See
`COMPILATION_REPORT.md` for the exact compiler versions, commands, warnings and
inspection notes.

## Directory layout

```text
paper/zenodo_preprint/
â”œâ”€â”€ input/
â”‚   â”œâ”€â”€ Manuscript.tex              # canonical manuscript
â”‚   â”œâ”€â”€ Supplementary.tex           # standalone supplement
â”‚   â”œâ”€â”€ References.bib              # verified BibTeX database
â”‚   â”œâ”€â”€ Figures/                    # publication figures (PDF + PNG)
â”‚   â””â”€â”€ Tables/                     # booktabs table fragments
â”œâ”€â”€ scripts_paper/                  # figure/claim/metadata build helpers
├── rc2_evidence/                   # read-only RC2 engineering evidence
â”œâ”€â”€ _Templates/                     # upstream class and bst (GPL-3.0-or-later)
â”œâ”€â”€ build.sh, Makefile, VERSION     # upstream build driver
â”œâ”€â”€ LICENSE                         # upstream GPL-3.0 licence
â”œâ”€â”€ README_TEMPLATE.md              # upstream README
â”œâ”€â”€ docs_template/                  # upstream documentation
â”œâ”€â”€ output/pdf/                     # compiled PDFs
â”œâ”€â”€ README.md                       # this file
â”œâ”€â”€ SOURCE_PROVENANCE.md            # template, data and figure provenance
â”œâ”€â”€ MANUSCRIPT_STATUS.md            # status, blockers, handoff
â”œâ”€â”€ COMPILATION_REPORT.md           # compiler/build/inspection record
â”œâ”€â”€ CLAIM_EVIDENCE_MATRIX.csv       # claim-by-claim traceability
â”œâ”€â”€ LITERATURE_MATRIX.md            # verified literature and positioning
â”œâ”€â”€ FIGURE_TABLE_REGISTER.md        # figure/table provenance and QA
â”œâ”€â”€ ZENODO_METADATA_DRAFT.md        # draft metadata; NOT uploaded
â””â”€â”€ REVISION_LOG.md                 # changes in this drafting round
```

## Evidence hierarchy used

1. Independently reproduced RC1 results (auditor re-audit, 20 November 2026).
2. Actual canonical RC1 tables and code (`data/processed/modeling/`,
   `outputs/tables/`, `outputs/remediation/tables/`).
3. RC1 integration evidence and handoff.
4. Independent auditor interpretation.
5. Agent handoffs.
6. Earlier exploratory statements.

Where sources disagreed, the manuscript follows the frozen RC1 arithmetic and
labels interpretation as provisional. The legacy 2,538-cell benchmark is
reported as legacy; the RC1 common set is 2,536 cells.

## What this draft does not claim

- It does not claim peer review, acceptance or publication.
- It does not claim verified 2024 Landsat acquisition lineage.
- It does not claim verified public park access or entrances.
- It does not claim that M4 is a validated vulnerability, health-risk or
  causal model.
- It does not claim that M4 is superior to M1â€“M3.
- It does not claim that the results are Jakarta-wide.
- It does not claim that local LISA clusters are causal.
- It does not claim that any intervention would be effective.

## Independent audit status

A separate independent scientific audit (20 November 2026) is in
`paper/independent_scientific_audit_2026-11-20/`. It confirms the core
arithmetic but finds a material Table 7 baseline-labelling defect and recommends
**HOLD** until that table is split/corrected and D4, D10 and RS-01 are signed.
Do not upload the current PDF to Zenodo.

## Next human decisions

The manuscript is deliberately a substantive draft, not a final scientific
release. The coordinator must resolve the decisions recorded in
`MANUSCRIPT_STATUS.md` before any public deposit. No Zenodo upload or DOI
request has been performed.

