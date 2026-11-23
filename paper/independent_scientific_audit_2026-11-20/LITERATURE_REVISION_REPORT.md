# Literature Revision Report

**Manuscript:** From Thermal Hotspots to Spatial Priorities: Attribution and
Sensitivity of Urban Heat Screening in Jakarta
**Date:** 21 November 2026
**Scope:** final related-work and novelty revision only. No GIS, model, score,
ranking or statistical output was recomputed or changed.

## 1. References incorporated

Six new references were verified and cited:

| Key | Reference | DOI | Verification |
|---|---|---|---|
| `perdinan2026` | Perdinan et al. (2026), *Spatial prioritization of vegetation-based climate adaptation pathways in tropical megacity Jakarta, Indonesia*, Scientific Reports 16:20857 | 10.1038/s41598-026-50579-y | Crossref metadata; open-access full text at Nature |
| `fitria2026` | Fitria, Tsai, You & Wang (2026), *Spatial disagreement as decision-support for district-level heat adaptation priorities: Evidence from Taiwan's six major cities*, Sustainable Cities and Society 148:107630 | 10.1016/j.scs.2026.107630 | Crossref metadata; ScienceDirect abstract/highlights; SAO/ADS abstract |
| `ramadhanis2026` | Ramadhanis, Anfaresi & Febriyanti (2026), *Spatial assessment of children's vulnerability to green space accessibility in Jakarta, Indonesia*, Jurnal Pengembangan Kota 14(1):72–83 | 10.14710/jpk.14.1.72-83 | Crossref metadata; open-access PDF |
| `dong2024` | Dong et al. (2024), *Measuring urban thermal environment from accessibility-based perspective: A case study in a populous city*, Geography and Sustainability 5(3):329–342 | 10.1016/j.geosus.2024.02.004 | Crossref metadata; open-access publisher page |
| `elmarakby2024` | Elmarakby & Elkadi (2024), *Prioritising urban heat island mitigation interventions: Mapping a heat risk index*, Science of the Total Environment 948:174927 | 10.1016/j.scitotenv.2024.174927 | Crossref metadata; PubMed abstract; publisher highlights |
| `ulfiasari2022` | Ulfiasari & Yola (2022), *Towards climate change adaptive spatial planning: Urban heat islands distribution in Jakarta Metropolitan Area*, Lecture Notes in Civil Engineering 243:111–118 | 10.1007/978-3-030-99979-7_13 | Crossref metadata; Universitas Indonesia repository abstract; Springer chapter metadata |

The existing `sobhaninia2025` review is now cited again in the revised
Introduction. The previously uncited `vargas2026` database entry was removed so
that the reference database and compiled bibliography are aligned.

## 2. Reference omitted

**Aghaloo & Sharifi (2025)**, *Integrated spatial prioritization of urban
nature-based solutions for climate adaptation, mitigation, and justice*,
International Journal of Sustainable Development & World Ecology 32(2):224–241,
DOI 10.1080/13504509.2024.2424988.

Reason: Crossref metadata was verified, but accessible material did not
establish a distinct methodological contribution beyond the composite,
prioritisation and sensitivity literature already represented. It was not added
merely to increase the bibliography.

## 3. Introduction and Related Work

- The Introduction now acknowledges Jakarta UHI mapping, regression-informed
  adaptation prioritisation, child-specific green-space vulnerability,
  accessibility-based thermal analysis, composite heat-risk indices and
  ranking-disagreement research.
- The research gap is narrower: sequential construct attribution, demographic
  count/share redundancy, the additive park threshold and candidate-park/network
  uncertainty.
- Related Work was revised by synthesis rather than paper-by-paper summary:
  - composite-index subsection now includes Elmarakby & Elkadi and Perdinan;
  - age/access subsection includes Ramadhanis and Dong;
  - sensitivity subsection includes Fitria and Perdinan;
  - Jakarta subsection includes Ulfiasari & Yola, Perdinan and Ramadhanis;
  - positioning explicitly states that neither the combination nor sensitivity
    analysis is new.
- No claim of being first to integrate indicators or first to analyse
  sensitivity remains.

## 4. Discussion

The discussion now includes a focused comparison with:

- **Perdinan et al. (2026):** regression-informed adaptation tiers and
  weight/threshold stability; compatible with our cell-level reprioritisation.
- **Fitria et al. (2026):** ranking disagreement as decision support; the
  Shapley decomposition is complementary, not a first.
- **Ramadhanis et al. (2026) and Dong et al. (2024):** demographic/accessibility
  precedents; our results concern screening-index behaviour, not verified public
  access or individual vulnerability.
- **Elmarakby & Elkadi (2024) and Ulfiasari & Yola (2022):** composite risk
  mapping and Jakarta UHI context; neither replaces the sequential attribution
  question.
- **Sidiqui et al. (2022), Kim & Kwak (2026), Fung et al. (2024):** existing
  narrower comparisons retained.

## 5. Table 1

Table 1 was reduced from ten rows to eight focused rows:

- Perdinan et al. (2026)
- Fitria et al. (2026)
- Ramadhanis et al. (2026)
- Dong et al. (2024)
- Elmarakby & Elkadi (2024)
- Ulfiasari & Yola (2022)
- Kim & Kwak (2026)
- This study

The table is footnotesize, uses six columns and is readable on the rendered
page. It is described as selective, not a systematic review.

## 6. Bibliography

- `References.bib`: **67 entries, 67 cited**.
- **64 cited entries carry DOI metadata**; **3 are no-DOI** (Oke 1984 book,
  OpenStreetMap snapshot, project documentation).
- No duplicate keys or duplicate DOIs.
- No undefined citations or references.
- The old uncited Vargas Molina entry was removed from the database.

## 7. Compilation and PDF inspection

Build command:

```bash
cd /d/jakarta-heat-paper/paper/zenodo_preprint
bash scripts_paper/build_final_candidate.sh
```

Results:

| PDF | Pages | Bytes | SHA-256 |
|---|---:|---:|---|
| `Manuscript-neutral.pdf` / package preprint | 25 | 2,426,183 | `72E4E50B60716408D3AE60A66DA1D422BD1A19E42D62F3D0A72660EB7553A986` |
| `Manuscript-internal-review.pdf` | 25 | 2,426,719 | `234BC4F7780D49A73844E4390B3E5FF04BFBB6B4C7876E2C6EDF2B1EBA0AB47B` |
| `Supplementary-neutral.pdf` / package supplement | 8 | 801,426 | `9CD990B91FDC94DAD04D5CE5663D42CD80920C8E9ECEC8908387133ACE096A58` |

- No undefined citations/references.
- No overfull hbox in the final main build.
- Table 1 and the new Discussion pages were rendered and inspected.
- PDF metadata remains correct: title, author order, subject and eight keywords.
- No empirical result, figure or table of results was altered.

## 8. Conclusion

The literature revision is complete. The manuscript now positions the work
honestly relative to the closest Jakarta and international studies and retains
only the contribution supported by its verified results. No material novelty or
citation problem was found that would require a HOLD.
