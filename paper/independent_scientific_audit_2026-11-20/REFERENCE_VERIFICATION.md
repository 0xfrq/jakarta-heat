# Reference Verification

**Date:** 20 November 2026
**BibTeX database:** `paper/zenodo_preprint/input/References.bib`
**Entries in database:** 62
**Entries cited in the compiled manuscript:** 61
**DOI-bearing entries checked:** 59
**No-DOI entries:** 3

The compiled PDF has 61 cited references. One database entry (Vargas Molina et
al., 2026) is a verified supporting lead but is not cited in the current text;
it is retained in the database but is not part of the 61-entry reference list.

## Method

- Parsed every BibTeX entry for title, authors, year, venue, volume, issue,
  pages and DOI.
- Resolved each DOI through `https://doi.org/<doi>` with CSL-JSON content
  negotiation and compared title, year, venue, volume, issue and pages.
- Checked the WorldPop dataset through DataCite (DOI
  `10.5258/SOTON/WP00841`) and the USGS Landsat dataset through DataCite (DOI
  `10.5066/P9OGBGM6`).
- Checked the no-DOI book, OpenStreetMap snapshot and internal artifact against
  their bibliographic/technical records.
- Did not invent missing metadata; fields that could not be verified are marked
  as such.

Machine-readable results:
`paper/independent_scientific_audit_2026-11-20/evidence/reference_verification.csv`.

## Result

- **59/59 DOI-bearing entries resolved.** No title, year (beyond the expected
  volume-year difference), volume or page mismatch was found in the checked
  fields.
- **No fabricated references.**
- **No placeholder citations.**

### WorldPop

Verified DataCite record:

- Title: *Estimates of 2015–2030 total number of people per grid square broken
  down by gender and age groupings at a resolution of 3 arc (approximately
  100 m at the equator), R2025A version v1.*
- DOI: `10.5258/SOTON/WP00841`
- Publisher: University of Southampton
- Year: 2025
- 13 creators, including Bondarenko, Priyatikanto, Tejedor Garavito, Zhang,
  McKeen, Cunningham, Woods, Hilton, Cihan, Nosatiuk, Brinkhoff, Tatem and
  Sorichetta.
- Resolution: 3 arc-second, approximately 100 m at the equator.
- Reference period in the manuscript: 2024 (the dataset covers 2015–2030).

The manuscript's “2024 reference year” and “≈100 m (3 arc-second)” statements
are consistent with the dataset metadata.

### Landsat

Verified DataCite record:

- Title: *Landsat 8-9 Operational Land Imager / Thermal Infrared Sensor Level-2,
  Collection 2*
- DOI: `10.5066/P9OGBGM6`
- Publisher: U.S. Geological Survey
- Year: 2020
- Creator: Earth Resources Observation and Science (EROS) Center.

The BibTeX entry was corrected from a product-guide URL to this dataset DOI.
The manuscript uses Landsat 9 Collection 2 Level-2; the dataset DOI covers
Landsat 8–9 OLI/TIRS Level-2 Collection 2.

### No-DOI entries

| Entry | Verification |
|---|---|
| `openshaw1984` — *The Modifiable Areal Unit Problem* | Book; CATMOG 38; Geo Books, Norwich, 1984. Bibliographic metadata consistent with the standard citation. No DOI. |
| `osm2026` — OpenStreetMap snapshot, 19 November 2026 | OpenStreetMap contributor data; ODbL; snapshot date and attribution are recorded. No DOI. |
| `jhim2026` — frozen RC1 research artifact | Internal project artifact; no public DOI; explicitly labeled as an internal, conditionally released research candidate. |

## Notes and minor issues

- **Vargas Molina et al. (2026)** is in the database and the literature matrix
  but is not cited in the compiled manuscript. Either cite it in the
  climate-shelter/access paragraph or remove it from the citation database and
  matrix. The reference list currently has 61 cited entries.
- **Sidiqui et al. (2022)** is a Greater Geelong, Australia study, not a Jakarta
  study. Table 1 should say so explicitly; the current “GIS-based urban case”
  is too vague.
- **Kim & Kwak (2026)** first author is **Wansu Kim** (verified via DOI record),
  not “Wan-Hyuk Kim”. The BibTeX entry is correct.
- **Tuholske et al. (2021)** is PNAS 118(41):e2024792118; the issue number in
  the DOI record is 41, not 34.
- **Peng et al. (2012)**, **Zhou et al. (2019)**, **Barron et al. (2014)**,
  **Paruolo et al. (2013)** and **Ekkel & de Vries (2017)** use the standard
  volume year rather than the online-first year; this is acceptable and
  consistent with the journal citations.
- Some `.bbl` entries lowercase `OpenStreetMap`, `Jakarta` or `R2025A` because
  the BibTeX fields are not braced. This is cosmetic; fix with braces if a
  final typesetting pass is desired.

## Verdict

**PASS with minor corrections.** The 61 cited references are verified against
authoritative DOI/dataset records. The remaining issues are bibliographic
polish (Vargas citation/removal, Sidiqui location, capitalization), not
fabricated or unsupported references.
