# Compilation Report

**Date:** 21 November 2026 (WIB)
**Workspace:** `D:\jakarta-heat-paper\paper\zenodo_preprint`
**Status:** publication-candidate and internal-review PDFs produced and inspected.
**Scientific status:** publication candidate; human author/release confirmation
still required.

## 1. Environment

| Item | Value |
|---|---|
| OS | Windows x64 |
| TeX distribution | TinyTeX / TeX Live 2026 (portable) |
| pdfTeX | 3.141592653-2.6-1.40.29 (TeX Live 2026) |
| latexmk | 4.88 (John Collins, 9 March 2026) |
| BibTeX | 0.99e (TeX Live 2026) |
| Template class | `_Templates/MultiTargetManuscript.cls`, v1.0.0 |
| Bibliography style | `_Templates/MultiTargetManuscript.bst` |
| Shell | Git Bash 5.3.15 (Cygwin) |
| Python used for figures | 3.12.10 (RC1 integration virtual environment) |

The system MiKTeX 25.12 installation was inspected earlier but not used for the
final build because its dependency preflight stalled. The portable TinyTeX
distribution compiled the same sources successfully.

## 2. Commands actually run

```bash
cd /d/jakarta-heat-paper/paper/zenodo_preprint
bash scripts_paper/build_final_candidate.sh
```

The wrapper runs:

```bash
./build.sh --target neutral --input-dir input --main Manuscript.tex
./build.sh --target neutral --input-dir input --main Manuscript-internal.tex
./build.sh --target neutral --input-dir input --main Supplementary.tex
cp output/pdf/Manuscript-neutral.pdf output/pdf/Manuscript-submission-candidate.pdf
cp output/pdf/Manuscript-internal-neutral.pdf output/pdf/Manuscript-internal-review.pdf
cp output/pdf/Supplementary-neutral.pdf output/pdf/Supplementary-submission-candidate.pdf
```

`Manuscript.tex` is the canonical scientific source. The neutral target is used
for the publication candidate so page footers do not imply a Zenodo deposit.
`Manuscript-internal.tex` is only a wrapper that adds the internal-review
identifier; it is not a second scientific source.

## 3. Outputs

| File | Pages | Size | SHA-256 |
|---|---:|---:|---|
| `Manuscript-submission-candidate.pdf` | 25 | 2,426,183 bytes | `72E4E50B60716408D3AE60A66DA1D422BD1A19E42D62F3D0A72660EB7553A986` |
| `Manuscript-internal-review.pdf` | 25 | 2,426,719 bytes | `234BC4F7780D49A73844E4390B3E5FF04BFBB6B4C7876E2C6EDF2B1EBA0AB47B` |
| `Supplementary-submission-candidate.pdf` | 8 | 801,426 bytes | `9CD990B91FDC94DAD04D5CE5663D42CD80920C8E9ECEC8908387133ACE096A58` |

Zenodo package copies (identical bytes to the neutral build):

- zenodo_release/Jakarta_Heat_Priorities_Preprint_v1.pdf — 25 pages, 2,426,183 bytes, SHA-256 72E4E50B60716408D3AE60A66DA1D422BD1A19E42D62F3D0A72660EB7553A986.
- zenodo_release/Jakarta_Heat_Priorities_Supplementary_v1.pdf — 8 pages, 801,426 bytes, SHA-256 9CD990B91FDC94DAD04D5CE5663D42CD80920C8E9ECEC8908387133ACE096A58.

SHA-256 of the canonical sources:

```text
input/Manuscript.tex        63CDAE94E51816D2B0705212F63A41F3C85B7E274D1D5323C4F97368DEA288FF
input/References.bib        CC6AA40A2B63CDC4931639827D69C405FBAC2B37830C45EEA7F66F87AB96793F
input/Supplementary.tex     02B1DB866EBB4B086BFCD3A517D8E77DBD6D1FD07E9535711EC036EE3E043A34
```

## 4. Bibliography and cross-references

- 67 cited references; no undefined citations.
- BibTeX resolved `_Templates/MultiTargetManuscript.bst`.
- No undefined references or multiply-defined labels in the final build.
- The USGS dataset is cited through DOI `10.5066/P9OGBGM6`; WorldPop through
  DOI `10.5258/SOTON/WP00841`.
- The reference database contains 67 entries, all cited. The compiled reference
  list has 67 entries.

## 5. Warnings and layout checks

- Main manuscript: no overfull `\hbox`; one underfull `\hbox` of
  badness 6927 in the declarations region; visually acceptable in the rendered PDF.
- Supplement: one overfull `\hbox` of **1.41 pt** caused by a long
  `Supplementary_Tables/...` path; not visible in the rendered PDF.
- No missing figures, missing tables, undefined citations or undefined
  references.
- Equation (7) is split into three lines and fits.
- Table 6 note now reports shared cells and retention separately from Jaccard.
- Table 7 (M3-relative) and Table 8 (M4-relative) are separate and labelled.
- Figure 6 and Table 10 use the adopted two-sided/9,999/BH LISA convention.
- PDF metadata: title, authors, subject and keywords are present; the clean PDF
  has no working-draft banner and no Zenodo acceptance/deposit claim.

## 6. Visual inspection

Rendered and inspected:

- clean title page and author/affiliation layout;
- Table 6 and the Jaccard/retention note;
- Table 7 and Table 8 attribution tables;
- LISA text, Figure 6 and Table 10;
- references pages, including USGS and WorldPop entries;
- supplement S2–S5 and S7–S9, including the 49-scenario long table and the
  primary LISA table;
- internal-review title page (concise internal identifier only).

The clean publication candidate is **25 pages**; the supplement is **8 pages**.
The page size is the template's letter-paper layout (612 × 792 pt), inherited
from the upstream class.

## 7. What was not done

- No Zenodo upload or DOI request.
- No claim of peer review, acceptance or publication.
- No author-consent claim; the author/release checklist is separate.
- No claim that original Landsat acquisition-level records were recovered.
