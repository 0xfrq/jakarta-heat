# Landsat Provenance Audit — RS-01

**Audit date:** 20 November 2026
**Frozen reference:** RC1 `3b8ed05be92c35bbb2b3a617688540ee856b11c8`
**Status:** **BLOCKED — original scene/task/AOI lineage unavailable**
**Narrow claim:** declared 2024 recipe period, not verified acquisition history

---

## 1. Scope

This audit examines whether the thermal/vegetation layer can be traced from the
original Landsat 9 Collection 2 Level-2 scenes through the Google Earth Engine
recipe to the delivered GeoTIFF, the grid table and the manuscript figures. It
does not attempt to fabricate or reconstruct scene identifiers.

Evidence inspected:

- `docs/landsat_metadata.json`
- `docs/remote_sensing_export_manifest.json`
- `docs/remote_sensing_scene_manifest.csv`
- `docs/remote_sensing_deliverable_status.md`
- `docs/remote_sensing_reproduction.md`
- `docs/landsat_quality_report.md`
- `scripts/02_remote_sensing_gee.js`
- `scripts/02b_aggregate_remote_sensing.py`
- `data/processed/remote_sensing/jakarta_2024_lst_ndvi_qa.tif`
- `data/processed/remote_sensing_remediated/remote_sensing_grid.csv`
- `data/processed/remote_sensing_remediated/remote_sensing_grid.meta.json`
- `data/processed/remote_sensing/remote_sensing_grid.meta.json` (if present)
- RC1 audit RS-01 findings and RC2 engineering handoff

---

## 2. What is verified

### 2.1 Raster identity and structure

The thermal GeoTIFF exists and is readable:

| Property | Value |
|---|---|
| Driver | GTiff |
| Size | 1,058 × 1,042 pixels |
| CRS | EPSG:32748 |
| Resolution | 30 m |
| Bands | `lst_c`, `ndvi`, `lst_unc_k`, `lst_obs`, `lst_valid` |
| Data type | float32 |
| Nodata | −9999 |
| Bounds | 686580, 9295410, 718320, 9326670 |
| SHA-256 | `f46d0db14f2f667a533eff7960bb870b4b2676709af43e70d08e670a075958dd` |

The GeoTIFF has **no scene/date/task metadata tags** beyond `AREA_OR_POINT =
Area`. The tags are not a provenance record.

### 2.2 Delivered grid

`remote_sensing_remediated/remote_sensing_grid.csv` has **2,765 rows** and
**zero missing LST/NDVI** values. The grid table has 42 columns, including
`lst_mean_c`, `ndvi_mean`, `lst_valid_fraction`, `lst_observation_count`,
`lst_std_c`, `lst_min_c`, `lst_max_c`, `lst_unc_mean_k` and Dynamic World
probability fields. The local raster-to-grid aggregation is reproducible from
the frozen GeoTIFF.

### 2.3 Intended recipe

`scripts/02_remote_sensing_gee.js` documents:

- Collection: `LANDSAT/LC09/C02/T1_L2`
- Period: 2024-01-01 to 2025-01-01 (exclusive)
- Processing level: L2SP
- QA mask: `QA_PIXEL` bits 0–5 == 0 and `QA_RADSAT == 0`
- LST: `ST_B10 * 0.00341802 + 149.0 − 273.15` °C
- NDVI: `(SR_B5 − SR_B4) / (SR_B5 + SR_B4)` with Collection 2 reflectance
  scaling
- ST_QA: `ST_QA * 0.01` K
- Composite: per-pixel median of clear observations
- Export: 30 m, EPSG:32748, nodata −9999
- AOI: `projects/nodemailer-mailer/assets/jakarta_5kota`

The recipe header explicitly says it is the **intended recipe**, not proof of the
historical acquisition identity.

### 2.4 Local reproduction

RC1 reports a PASS for the local raster-to-grid reproduction:
`local_reproduction_status = PASS_FROZEN_RASTERS_TO_GRID`. This verifies that the
delivered grid values can be regenerated from the frozen GeoTIFF. It does not
verify the GeoTIFF's original scenes.

### 2.5 Annual support

Annual clear-observation counts are available (grid mean 5.96–27.4 observations
per pixel; pixel counts 3–28). These counts describe temporal support but do not
identify acquisition dates or seasons.

---

## 3. What is missing

### 3.1 Scene manifest

`docs/remote_sensing_scene_manifest.csv` is **header-only**: 0 data rows. The
export manifest states:

```json
"scene_manifest_validation": {
  "state": "BLOCKED",
  "n_scenes": 0,
  "reason": "No recovered scene records; zero rows is not zero acquisitions"
}
```

This is a critical distinction: 0 rows means **records unavailable**, not
**zero scenes**. No scene IDs, acquisition dates, WRS path/row, product IDs,
L2SP flags or source product-generation metadata are present.

### 3.2 Task and AOI

`docs/remote_sensing_export_manifest.json` records:

- `task_id: null`
- `processing_date_utc: null`
- `scene_ids_verified: false`
- AOI equivalence to the GEE asset: `UNVERIFIED; local hash is not a historical
  GEE AOI hash`

No original GEE task JSON, task status, completion timestamp or versioned AOI
geometry is available. The local AOI hash cannot substitute for the historical
GEE AOI identity.

### 3.3 Temporal support

The median raster cannot recover monthly or seasonal sampling. The number of
clear observations per pixel is known, but the dates are not. Therefore:

- no seasonal representativeness claim;
- no annual mean claim;
- no temporal trend claim;
- no “2024 snapshot” claim in the sense of a verified acquisition date.

### 3.4 Historical OSM

Six historical OSM requests failed (HTTP 406); no 2024 OSM snapshot exists. This
is a separate temporal limitation (TM-02), but it compounds the mixed-period
interpretation: the thermal layer is 2024-declared and the network is 2026.

### 3.5 Authentication

No Google Earth Engine authentication was available in the audit environment.
No credentials were copied, no task was submitted, and no replay was attempted.
This is an external block, not a negative result.

---

## 4. What the manuscript currently claims

The manuscript correctly states:

- 2024 is a **declared recipe period**, not a verified acquisition history.
- The scene/task/AOI records are unavailable.
- The annual clear-observation counts do not establish seasonal
  representativeness.
- LST is a surface temperature, not air temperature or personal exposure.
- The analysis is a mixed-period candidate proxy.

The Figure 1 caption says “LST is the declared 2024 clear-sky morning median.”
The abstract says “Thermal and demographic inputs refer to a declared 2024
period.” These are appropriate.

**Risk:** the title, abstract and conclusion still use “2024” as a shorthand.
Readers may interpret it as verified. The paper should consistently say
“declared 2024 thermal period” or “2024-declared composite” in the abstract,
Methods, figures and data availability. The phrase “verified 2024” must not
appear.

---

## 5. Narrowest scientifically defensible claim

> The thermal/vegetation layer is a **declared 2024 clear-sky morning median
> composite** derived from Landsat 9 Collection 2 Level-2 using the intended
> Google Earth Engine recipe. The local raster-to-grid aggregation is
> reproducible from the frozen export. The original scene/task/AOI lineage is
> unavailable; the 2024 label is a recipe period, not an independently verified
> acquisition history. No annual, seasonal, trend, air-temperature or
> personal-exposure claim is supported.

This claim is sufficient for an exploratory screening preprint **if** it is
stated consistently and the manuscript does not imply verified acquisition.

---

## 6. Evidence required to close RS-01

A complete closure requires:

1. Scene/product IDs for every Landsat 9 L2SP scene used.
2. UTC acquisition dates and WRS path/row.
3. L2SP flags and source product-generation metadata.
4. GEE task IDs, task status, completion timestamps and error state.
5. Exact AOI geometry, version/hash and export parameters.
6. Monthly clear-observation counts and a seasonal support summary.
7. A recipe/task JSON archive tied to the exported GeoTIFF hashes.
8. Independent comparison of the replayed scene inventory with the frozen
   raster (not just a local array comparison).

If any of these are unavailable, a **signed claim restriction** is required. The
restriction should state:

- “2024” is a declared recipe period;
- no annual/seasonal/trend claim;
- no 2024 public-access claim;
- no 2026 heat claim;
- the thermal layer is a surface-temperature proxy, not air temperature or
  personal exposure.

---

## 7. Audit verdict

| Gate | Verdict |
|---|---|
| Raster readability and local aggregation | **PASS** |
| Intended recipe documentation | **PASS** |
| Scene/date/task/AOI lineage | **BLOCKED** |
| Seasonal/annual representativeness | **NOT ESTABLISHED** |
| Claim restriction in manuscript | **MOSTLY PRESENT; needs consistency edit** |
| Overall RS-01 | **HOLD / BLOCKED** |

**Recommendation:** do not attempt to close RS-01 by assertion. Either recover
the evidence or sign the narrow claim restriction. The manuscript can be a
defensible exploratory preprint under the restriction; it cannot claim verified
2024 acquisition or seasonal representativeness.
