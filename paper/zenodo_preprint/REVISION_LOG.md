# Revision Log

**Manuscript:** From Thermal Hotspots to Spatial Priorities
**Branch:** `paper/zenodo-draft`
**Base revision:** `3b8ed05be92c35bbb2b3a617688540ee856b11c8`
**Log started:** 20 November 2026

## 2026-11-20 — Initial full draft

### Template and workspace

- Inspected Zenodo record `22018962` and upstream
  `raramayo/Manuscripts_Templates_Latex`.
- Downloaded `Manuscripts_Templates_Latex-v1.0.0.zip` (SHA-256
  `815c28eeea8daa88f7874195a65ed264ee55c811d724f45b0fc05b0d0a91f877`).
- Installed the template's shared class and bibliography style under
  `_Templates/`; retained `LICENSE`, `README_TEMPLATE.md`, `docs_template/`.
- Established `input/Manuscript.tex` as the single canonical source.
- Added `input/Supplementary.tex` as a standalone supplement.

### Scientific evidence

- Read the independent RC1 re-audit (`RC1_REAUDIT_REPORT.md`,
  `RC1_ISSUE_CLOSURE_MATRIX.csv`, `RC1_RELEASE_GATE.md`,
  `RC1_SCIENTIFIC_DECISIONS.md`, `RC1_NOVELTY_EVIDENCE.md`,
  `RC1_REMAINING_TASKS.md`, `RC1_VERIFICATION_LOG.md`,
  `RC1_EXECUTIVE_SUMMARY.md`).
- Read the RC1 handoff, verification, reproduction instructions, model
  specification, spatial inference specification, park policy, population
  aggregation method and demographic support semantics.
- Used RC1 as the frozen reference; RC2 outputs were not substituted.
- Confirmed key arithmetic directly from RC1 tables: 2,765 master; 2,536 common;
  254 top budget; Jaccard M1–M4 0.384; M3–M4 0.411; Shapley 85.46/13.25/1.29;
  cutoff 0.873739849; max near-park 0.869648776; 0/537; top minimum 638.2 m;
  174/254 at cap; LISA 663/496/687/493/0/284/234.

### Manuscript content

- Wrote title, author block, draft banner, abstract, keywords, correspondence.
- Wrote Sections 1–8, Data and Code Availability, Author Contributions, Funding,
  Conflicts, Acknowledgements, Supplementary Material.
- Added exact M1–M4 equations, normalisation, Jaccard, Shapley decomposition,
  Moran/LISA conventions, scenario definitions and eligibility rules.
- Added 17 specific limitations, including RS-01, LST vs air temperature,
  mixed periods, OSM coverage, unverified access/entrances, network snapping,
  missing routes, demographic support, partial coastal cells, weights,
  selection, LISA conventions, causal limits and software portability.
- Removed/qualified unsupported claims: age-vulnerability, park-inequality
  discovery, model superiority, Jakarta-wide, p=0, verified public access,
  health/intervention effects, and "first integrated framework".

### Literature

- Built a 61-entry BibTeX database from verified DOI/publisher metadata.
- Added a focused literature matrix and explicit positioning: combination-only
  novelty is rejected; contribution is attribution/uncertainty/negative
  findings/reproducibility.
- Did not cite unverified Rahman et al. (2026) metadata; documented this in the
  literature matrix.

### Figures and tables

- Generated publication figures from RC1 tables/GIS: study area/environment,
  population/access, M1/M4 priority maps, rank displacement, Shapley/sensitivity,
  LISA, and supplementary score/exclusion/park-inventory figures.
- Added 10 main tables and 6 supplementary tables.
- Fixed caption/float collisions found during PDF inspection by using `[H]`
  placement for Tables 6 and 7 and increasing `\belowcaptionskip`.

### Build and layout

- System MiKTeX 25.12 dependency preflight hung; switched to portable
  TinyTeX/TeX Live 2026 for the build.
- Built `Manuscript-zenodo.pdf` (23 pages), `Manuscript-neutral.pdf` (23 pages)
  and `Supplementary-zenodo.pdf` (6 pages).
- Fixed equation (7) overflow by splitting it into three lines.
- Wrapped long commit/implementation hashes with `seqsplit`.
- Added a `References` heading and cleared the running header for the reference
  pages.
- Visually inspected the rendered PDFs; remaining overfull box is 2.03 pt and
  not material.

### Author metadata update

- Replaced author placeholders with:
  - Muhammad Fariq Faqih (`fariq@renaro.my.id`)
  - Muhammad Alim Mustofa (`alim@renaro.my.id`)
  - Mu'adz Abdulloh (`muadz@renaro.my.id`)
- Affiliation: Renaro Lab, student-led independent AI laboratory,
  <https://renaro.my.id>.
- Corresponding author marker currently on Muhammad Fariq Faqih; ORCIDs remain
  to be added if the authors wish.

## 2026-11-20 — Independent scientific audit (post-draft)

- Added a separate audit workspace at
  `paper/independent_scientific_audit_2026-11-20/`.
- Independently recomputed scores, ranks, Jaccard, Shapley, cutoff, selection,
  LISA and scenario-family ranges from RC1 tables.
- Found a material Table 7 baseline-labelling defect: rows 15–20 are
  M3-relative, while the caption/footnote state M4-relative. The underlying
  arithmetic is verified; the table presentation is blocked.
- Updated `CLAIM_EVIDENCE_MATRIX.csv` C33 to state the M3 baseline and added
  C39 (BLOCKED) for the Table 7 caption/footnote claim.
- Updated `MANUSCRIPT_STATUS.md`, `FIGURE_TABLE_REGISTER.md`, `README.md` and
  `ZENODO_METADATA_DRAFT.md` with the HOLD flag.
- No manuscript text, model, weight, threshold or dataset was changed by the
  audit.

## 2026-11-20 — Final manuscript corrections (RC2 engineering evidence)

- Corrected Jaccard interpretation throughout: 141/254 is **55.5% retention**,
  not 38.4% shared membership; Jaccard 0.384 is shared cells divided by the
  union (367). Updated abstract, Results, Discussion and Conclusion; added
  shared/retention counts to the Table 6 note.
- Split the old attribution table into Table 7 (incremental effects relative to
  M3) and Table 8 (construct/ablation comparisons relative to M4). Updated text,
  captions, claim matrix and figure/table register.
- Updated engineering limitations and Data and Code Availability with verified
  RC2 evidence: clean-checkout 236 tests + 7 subtests, 0 failures/errors/skips;
  RC1 and RC2 receipts 9/9 under canonical Git-blob SHA-256; standard and
  remediation manifests 69/69 and 80/80 relative; 63-table replay max difference
  0.0. Empirical results remain RC1; RC2 is engineering remediation, not
  scientific approval.
- Added supplementary S6 full scenario results (49 rows), S7 demographic
  no-support table, S8 eligibility reconciliation, and updated S9 provenance;
  added machine-readable CSVs under `input/Supplementary_Tables/`.
- Verified 58 DOI-bearing references via DOI content negotiation; updated the
  USGS reference to the authoritative Landsat 8-9 C2 L2 dataset DOI
  `10.5066/P9OGBGM6`. Four no-DOI entries are documented (book, USGS dataset,
  OSM snapshot, internal RC1 artifact).
- Removed the `\Letter` corresponding-author glyph from the first author to
  eliminate the stray superscript; correspondence is given in the
  `corrauthor` line.
- Added an explicit statement that the Zenodo footer profile is a presentation
  format, not a deposit, submission, acceptance or DOI.
- PDF metadata title/author/keywords were already set via `\hypersetup`;
  unchanged and rechecked after rebuild.

## Open items (not changed in this round)

- Scientific decisions D1–D12 remain unsigned.
- M4 remains a provisional exposure-oriented screening index; no final relabel
  decision has been signed.
- RS-01 Landsat lineage remains blocked; the manuscript uses "declared 2024
  recipe period".
- Park access/entrances remain unverified; no field audit was performed.
- RC2 is not integrated.
- No Zenodo upload or DOI request was made.
- Author Contributions and funding/conflict statements require human approval.

## 2026-11-21 — Revisi editorial publication candidate

- Menerapkan D1–D13 pada naskah: periode campuran 2024/2026, M4 sebagai
  exploratory heat–population–park-deficit screening index, age count sebagai
  model utama dan age share sebagai sensitivitas, hybrid allocation sebagai
  baseline, serta kandidat taman sebagai proxy akses.
- Mengganti konvensi LISA utama menjadi two-sided, 9.999 permutations,
  Benjamini–Hochberg q = 0,05. Peta dan Tabel 10 dibangun dari output per-sel
  (lisa_m4_primary.csv), bukan dari total agregat. Hasil utama: 493 sel
  signifikan (HH 252, LL 227, HL 7, LH 7; 2.042 tidak signifikan).
- Memisahkan Tabel 7 (relatif M3) dan Tabel 8 (relatif M4); memperbaiki seluruh
  interpretasi Jaccard/retention: 141/254 = 55,5%; Jaccard 0,384; union 367.
- Menghapus banner draft, istilah RC1/RC2 dalam narasi ilmiah, status unsigned,
  release-gate, claim-evidence register dan bahasa handoff dari PDF publik.
- Memendekkan abstrak menjadi ±260 kata; memperbaiki alur kontribusi, author
  affiliation, korespondensi, data availability, acknowledgements dan metadata.
- Menyusun PDF publication candidate 23 halaman, internal review 23 halaman dan
  suplemen 7 halaman; sumber SVG/PDF figure LISA diperbarui.
- Status akhir: publication candidate lengkap secara teknis; konfirmasi author,
  funding, konflik kepentingan, lisensi dan penerimaan limitasi provenance masih
  diperlukan. Tidak ada upload Zenodo, DOI request, commit atau push.

## 2026-11-21 — Final Zenodo preprint package

- Menambahkan Author Contributions kolektif, Funding, Conflicts of Interest,
  Data and Code Availability yang direvisi, Use of AI-Assisted Tools, dan
  pernyataan CC BY 4.0 ke manuscript dan supplement.
- Menetapkan Muhammad Fariq Faqih sebagai corresponding author; urutan tiga
  author dan afiliasi Renaro Lab, Indonesia sesuai konfirmasi koordinator.
- Menambahkan catatan lisensi komponen: manuscript/figur/narasi suplemen CC BY
  4.0; template GPL-3.0-or-later; dataset pihak ketiga tetap pada lisensinya.
- Menyiapkan paket zenodo_release/ berisi dua PDF final, metadata draft,
  license, README dan manifest SHA-256.
- PDF final: publication candidate 24 halaman; supplement 8 halaman. Tidak ada
  undefined citation/reference.
- Status: ZENODO PACKAGE READY — AWAITING MANUAL UPLOAD; tidak ada upload,
  DOI request, commit atau push.

## 2026-11-21 — Final literature revision

- Memverifikasi dan menambahkan Perdinan et al. (2026), Fitria et al. (2026),
  Ramadhanis et al. (2026), Dong et al. (2024), Elmarakby dan Elkadi (2024),
  serta Ulfiasari dan Yola (2022).
- Menyusun ulang Table 1 menjadi delapan baris terfokus; memperbarui Introduction,
  Related Work dan Discussion agar tidak mengklaim kombinasi atau sensitivitas
  sebagai hal yang baru.
- Bibliografi final: 67 entri, 67 cited; 64 DOI-bearing dan 3 no-DOI.
- Opsional Aghaloo dan Sharifi (2025) tidak dimasukkan karena tidak ada
  kontribusi metodologis berbeda yang dapat diverifikasi dari akses yang tersedia.
- PDF final 25 halaman; supplement 8 halaman; tidak ada undefined citation.
- Paket Zenodo, metadata, license, README dan SHA-256 manifest diperbarui.
- Status: ZENODO PACKAGE READY — FINAL LITERATURE REVISION COMPLETE.
