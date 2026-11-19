/**
 * JAKARTA HEAT INEQUALITY MAPPER - PERSON 1 / AGENT 1
 * Job 4: Dynamic World V1 annual modal land-cover label, 2024.
 * Google Earth Engine Code Editor (JavaScript).
 *
 * WHY: scripts/02_remote_sensing_gee.js exported only the per-pixel MEDIAN of the
 * `trees` and `built` class probabilities. Probabilities are not area fractions and
 * there is no `grass` band. Class fractions per 500 m cell need a per-pixel class label.
 *
 * WHAT: per-pixel MODE of the per-image Dynamic World `label` band over
 * 2024-01-01 .. 2025-01-01 (end exclusive). Class codes (official DW order):
 *   0 water, 1 trees, 2 grass, 3 flooded_vegetation, 4 crops,
 *   5 shrub_and_scrub, 6 built, 7 bare, 8 snow_and_ice.
 * Pixels with no Dynamic World observation in 2024 are written as 255 (nodata).
 * ee.Reducer.mode() resolves ties deterministically (lowest value); document if used.
 *
 * OUTPUT (Google Drive, folder Jakarta_Heat_Project):
 *   jakarta_2024_dw_label_mode.tif  -- 1 band `label_mode`, UInt8, 10 m, EPSG:32748, nodata 255
 *   jakarta_2024_dw_obs_count.tif   -- 1 band `dw_obs`, UInt16, 10 m (diagnostic, optional)
 *
 * AFTER EXPORT: download the .tif files into data/processed/remote_sensing/ and run
 *   python scripts/02b_aggregate_remote_sensing.py
 * which then fills tree_fraction, grass_fraction, built_fraction, ... in
 * data/processed/remote_sensing_grid.csv. Do not commit the GeoTIFFs if they are large.
 *
 * Grid alignment: the export uses the same CRS/scale/AOI as the existing DW probability
 * export, so pixels align with jakarta_2024_trees_built_probability.tif.
 */

var YEAR = 2024;
var START = YEAR + '-01-01';
var END = (YEAR + 1) + '-01-01';
var BOUNDARY_ASSET = 'projects/nodemailer-mailer/assets/jakarta_5kota';
var EXPORT_FOLDER = 'Jakarta_Heat_Project';

var roi = ee.FeatureCollection(BOUNDARY_ASSET).geometry();
Map.centerObject(roi, 10);

var dwCol = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1')
  .filterBounds(roi)
  .filterDate(START, END);
print('Dynamic World images intersecting AOI, 2024:', dwCol.size());

var labelMode = dwCol.select('label')
  .reduce(ee.Reducer.mode())
  .rename('label_mode')
  .clip(roi);
var dwObs = dwCol.select('label').count().rename('dw_obs').clip(roi);

var dwVis = {min: 0, max: 8, palette: [
  '419bdf', '397d49', '88b053', '7a87c6', 'e49635',
  'dfc35a', 'c4281b', 'a59b8f', 'b39fe1']};
Map.addLayer(labelMode, dwVis, 'DW 2024 modal label');
Map.addLayer(dwObs, {min: 0, max: 60, palette: ['white', 'purple']}, 'DW obs count', false);

// Quick QA: class shares over the AOI at 30 m sampling (approximate).
print('Approx. AOI class histogram (30 m):', labelMode.reduceRegion({
  reducer: ee.Reducer.frequencyHistogram(), geometry: roi, scale: 30,
  maxPixels: 1e9, tileScale: 4}));
print('DW obs count min/max/mean (30 m):', dwObs.reduceRegion({
  reducer: ee.Reducer.minMax().combine({reducer2: ee.Reducer.mean(), sharedInputs: true}),
  geometry: roi, scale: 30, maxPixels: 1e9, tileScale: 4}));

Export.image.toDrive({
  image: labelMode.unmask(255).toUint8(),
  description: 'JKT_2024_DW_label_mode',
  folder: EXPORT_FOLDER,
  fileNamePrefix: 'jakarta_2024_dw_label_mode',
  region: roi,
  scale: 10,
  crs: 'EPSG:32748',
  maxPixels: 1e10,
  fileFormat: 'GeoTIFF',
  formatOptions: {noData: 255}
});

Export.image.toDrive({
  image: dwObs.unmask(0).toUint16(),
  description: 'JKT_2024_DW_obs_count',
  folder: EXPORT_FOLDER,
  fileNamePrefix: 'jakarta_2024_dw_obs_count',
  region: roi,
  scale: 10,
  crs: 'EPSG:32748',
  maxPixels: 1e10,
  fileFormat: 'GeoTIFF'
});
