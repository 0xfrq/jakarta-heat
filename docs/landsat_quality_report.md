
# Landsat 9 Quality Assessment Report

## Jakarta Heat Inequality Mapper

**Study Area:** Five Administrative Cities of Jakarta, Indonesia  
**Analysis Period:** January 1 – December 31, 2024  
**Dataset:** USGS Landsat 9 Collection 2 Level-2  
**Processing Platform:** Google Earth Engine  
**Status:** Preliminary Quality Assessment

---

## 1. Data Source

Satellite imagery was obtained from the USGS Landsat 9
Collection 2 Level-2 dataset, accessed through Google
Earth Engine.

- Dataset ID: `LANDSAT/LC09/C02/T1_L2`
- Processing Level: L2SP
- Temporal Coverage: January–December 2024
- Study Area: Five Administrative Cities of Jakarta
- Export CRS: EPSG:32748
- Export Resolution: 30 meters
- Composite Method: Median

Dataset documentation:
https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC09_C02_T1_L2

## 2. Preprocessing Methodology

The following preprocessing procedures were applied:

1. Filter Landsat 9 imagery to the 2024 study period.
2. Filter imagery by Jakarta's administrative boundary.
3. Select images with L2SP processing level.
4. Mask clouds, cloud shadows, cirrus, snow, fill,
   and radiometrically saturated pixels.
5. Apply Landsat Collection 2 scaling factors.
6. Calculate Land Surface Temperature (LST) in Celsius.
7. Calculate NDVI using red and near-infrared bands.
8. Generate median composites from valid observations.
9. Calculate valid observation counts and QA indicators.

### 2.1 Land Surface Temperature

LST was calculated using the ST_B10 band:

LST (°C) = ST_B10 × 0.00341802 + 149 - 273.15

### 2.2 Normalized Difference Vegetation Index

NDVI was calculated using the scaled surface
reflectance bands:

NDVI = (NIR - RED) / (NIR + RED)

Where:
- RED: SR_B4
- NIR: SR_B5

### 2.3 Surface Temperature Uncertainty

The ST_QA band was scaled by 0.01 to obtain the
per-observation surface temperature uncertainty
indicator in Kelvin.

The reported composite ST_QA summary must not be
interpreted as uncertainty of the annual median LST.

---

## 3. Preliminary Quality Assessment Results

Statistics were calculated in Google Earth Engine
using approximately 100-meter spatial sampling.

### 3.1 Land Surface Temperature

| Statistic | LST (°C) |
|---|---:|
| Minimum | 29.649 |
| P5 | 36.312 |
| P25 | 40.063 |
| Median (P50) | 41.937 |
| P75 | 43.438 |
| P95 | 45.309 |
| P99 | 46.557 |
| Maximum | 56.923 |

The annual median composite has a spatial median
LST of approximately 41.94 °C.

The maximum observed composite value is substantially
higher than the 99th percentile. Extreme pixels
require additional spatial and quality inspection.

### 3.2 NDVI

| Statistic | NDVI |
|---|---:|
| Minimum | -0.272 |
| P5 | 0.129 |
| P25 | 0.199 |
| Median (P50) | 0.277 |
| P75 | 0.402 |
| P95 | 0.637 |
| P99 | 0.746 |
| Maximum | 0.858 |

All reported NDVI values fall within the
theoretical range of -1 to 1.

### 3.3 Surface Temperature QA Indicator

| Statistic | Uncertainty (K) |
|---|---:|
| Minimum | 2.780 |
| P5 | 3.031 |
| P25 | 3.345 |
| Median (P50) | 3.594 |
| Mean | 3.636 |
| P75 | 3.843 |
| P95 | 4.343 |
| P99 | 4.966 |
| Maximum | 11.865 |

The relatively high maximum uncertainty indicator
suggests that some pixels require further inspection.

### 3.4 Valid Observations

| Statistic | Value |
|---|---:|
| Minimum | 5 |
| Mean | 10.818 |
| Maximum | 28 |

The median composite was constructed from varying
numbers of valid observations across the study area.

### 3.5 Valid LST Coverage

Approximate valid LST coverage:

**99.991%**

This represents the approximate spatial proportion
of sampled pixels with at least one valid LST
observation in the annual composite.

It does not represent the proportion of cloud-free
observations throughout the year.

---

## 4. Preliminary Assessment

The initial results indicate that:

1. NDVI values fall within the expected theoretical range.
2. LST values are physically plausible for urban surfaces,
   although extreme pixels require inspection.
3. Most sampled pixels contain valid LST observations.
4. The ST_QA indicator shows variability in retrieval
   uncertainty across the study area.
5. The resulting composite is suitable for further
   exploratory spatial analysis.

These findings do not constitute independent
ground-based validation of satellite temperature.

---

## 5. Limitations

- LST represents surface temperature, not air temperature.
- The annual median is not an annual mean temperature.
- Landsat thermal measurements have a coarser native
  resolution than the 30-meter output grid.
- Cloud contamination and retrieval errors may remain.
- ST_QA describes product-level retrieval uncertainty,
  not statistical uncertainty of the annual composite.
- QA statistics were approximated at 100-meter sampling.
- Extreme temperature pixels require further inspection.
- Seasonal and temporal sampling differences may affect
  interpretation.

---

## 6. Pending Validation

Status updated 2026-11-19 by Agent 1 using the full-resolution exported GeoTIFF
(not 100 m sampling). Details: `handoff/AGENT1_HANDOFF.md`,
`outputs/qa/remote_sensing_qa.json`.

- [x] Inspect spatial locations of extreme LST values. Pixel maximum 57.08 °C lies in
      grids JKT_R054_C056/C057 (Cilincing–Marunda industrial/port area, Jakarta Utara);
      56.56 °C in JKT_R044_C054 (Pulogadung industrial estate). Plausible for large
      industrial roofs and paved yards; values were kept, not clipped. Grid-level means
      (500 m) range 31.12–47.92 °C.
- [x] Evaluate pixels with high ST_QA uncertainty. 12 of 2,765 grids have mean
      (median-composite) ST_QA > 5 K, concentrated on the northern coast/industrial zone;
      flagged `high_unc` in `remote_sensing_grid.csv`.
- [x] Evaluate areas with low valid observation counts. Full-resolution per-pixel
      clear-observation count ranges 3–28; grid means 5.96–27.4. The southern strip
      has ~20–27 clear observations versus ~8–12 elsewhere (WRS-2 scene overlap), so
      temporal support of the median is not spatially uniform. No grid has mean < 5.
- [x] Check exported GeoTIFF bands and NoData handling. 5 bands, Float32, EPSG:32748,
      30 m. Outside the AOI is NaN (384,002 px); inside the AOI, -9999 marks the 78 px
      with no clear LST observation (`lst_valid == 0`), where NDVI is still valid.
      No scaled ST fill value (≈ -124 °C) is present. Pixel NDVI range -0.330 to 0.865.
- [x] Verify raster coverage against the final AOI. Every master-grid cell has
      Landsat footprint ≥ 98.9 % of its (clipped) area; valid-LST area fraction ≥ 0.278
      (minimum in edge cell JKT_R037_C062, the 78 px gap at the eastern boundary).
- [ ] Perform sensitivity analysis if needed (e.g. dry-season composite) — requires
      Earth Engine access; not done.
- [ ] Document total Landsat scene count — requires Earth Engine access
      (`landsatRaw.size()` is printed by the script but was not recorded).
      Observed per-pixel maximum of 28 clear observations is a lower bound for scenes
      used in the overlap zone.

---

## 7. Expected Output

Primary output:

`jakarta_2024_lst_ndvi_qa.tif`

Expected bands:

1. `lst_c`
2. `ndvi`
3. `lst_unc_k`
4. `lst_obs`
5. `lst_valid`

The raster will be aggregated to Jakarta's 500-meter
master grid for subsequent heat inequality modeling.

---

## 8. References

Google Earth Engine Data Catalog.
USGS Landsat 9 Collection 2 Tier 1 Level-2.

https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC09_C02_T1_L2

USGS Landsat Collection 2 Surface Temperature.

https://www.usgs.gov/landsat-missions/landsat-collection-2-surface-temperature
